-- OpsMind AI - Phase 2: Database Schema & Supabase Setup
-- DDL Script for PostgreSQL (Supabase)

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -------------------------------------------------------------
-- 1. Table Creation
-- -------------------------------------------------------------

-- Users table (authentication & authorization control)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Manager', 'Operator')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Products table (master catalog metadata)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0.00),
    reorder_level INTEGER NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inventory table (real-time stock quantities tracker)
CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID UNIQUE NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    stock_on_hand INTEGER NOT NULL DEFAULT 0 CHECK (stock_on_hand >= 0),
    allocated_stock INTEGER NOT NULL DEFAULT 0 CHECK (allocated_stock >= 0),
    reserved_stock INTEGER NOT NULL DEFAULT 0 CHECK (reserved_stock >= 0),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table (immutable historical stock movement ledger)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity <> 0),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('INBOUND', 'OUTBOUND', 'ADJUSTMENT', 'RETURNS')),
    reference_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Forecasts table (future predictive inventory data cached from ML runs)
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    forecast_quantity NUMERIC(12, 2) NOT NULL CHECK (forecast_quantity >= 0.00),
    confidence_lower NUMERIC(12, 2) NOT NULL CHECK (confidence_lower >= 0.00),
    confidence_upper NUMERIC(12, 2) NOT NULL CHECK (confidence_upper >= 0.00),
    model_engine VARCHAR(50) NOT NULL CHECK (model_engine IN ('Prophet', 'XGBoost')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_confidence_bounds CHECK (confidence_lower <= confidence_upper)
);

-- -------------------------------------------------------------
-- 2. Indexes for Performance Optimization
-- -------------------------------------------------------------

-- Users table searches
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Products sku lookup
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- Inventory foreign key lookup
CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);

-- Transactions listing by product and date
CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

-- Forecasts queries (essential for time series forecasting graphs)
CREATE INDEX IF NOT EXISTS idx_forecasts_product_id_date ON forecasts(product_id, forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON forecasts(forecast_date);

-- -------------------------------------------------------------
-- 3. Automated Inventory Sync Trigger Function
-- -------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_inventory_on_transaction()
RETURNS TRIGGER AS $$
DECLARE
    delta INTEGER;
BEGIN
    -- Determine dynamic stock adjustment value depending on the transaction type
    IF NEW.transaction_type = 'INBOUND' OR NEW.transaction_type = 'RETURNS' THEN
        delta := ABS(NEW.quantity);
    ELSIF NEW.transaction_type = 'OUTBOUND' THEN
        delta := -ABS(NEW.quantity);
    ELSIF NEW.transaction_type = 'ADJUSTMENT' THEN
        delta := NEW.quantity; -- Signed (+ or -) change based on manual adjustment details
    ELSE
        delta := 0;
    END IF;

    -- Update existing stock levels or insert new initial record if product's first transaction
    INSERT INTO inventory (product_id, stock_on_hand, allocated_stock, reserved_stock, updated_at)
    VALUES (NEW.product_id, GREATEST(0, delta), 0, 0, NOW())
    ON CONFLICT (product_id)
    DO UPDATE SET
        stock_on_hand = GREATEST(0, inventory.stock_on_hand + delta),
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------------------
-- 4. Trigger Initialization
-- -------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_after_transaction_insert ON transactions;

CREATE TRIGGER trg_after_transaction_insert
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_inventory_on_transaction();
