# OpsMind AI - Phase 2 Verification Checklist & Stage-Gate Exit Criteria

This document outlines the detailed verification criteria to validate that the Database Schema Design & Supabase integration have been successfully deployed and are ready for Phase 3.

---

## 📋 1. PostgreSQL Schema Validation (Supabase)
Log in to the **Supabase Dashboard** -> **Table Editor** / **SQL Editor** and verify:

- [ ] **Table Presence**: The following 5 tables are listed:
  - `users`
  - `products`
  - `inventory`
  - `transactions`
  - `forecasts`
- [ ] **Data Types & Primary Keys**:
  - All tables utilize a `UUID` as primary key (`id`) with a default generator `gen_random_uuid()`.
  - `unit_price` and `forecast_quantity`/`confidence_lower`/`confidence_upper` use a precision numeric type (e.g. `NUMERIC(10,2)` or `NUMERIC(12,2)`).
- [ ] **Cascading Rules**:
  - `inventory.product_id`, `transactions.product_id`, and `forecasts.product_id` possess foreign key relationships referencing `products.id` with `ON DELETE CASCADE`.
- [ ] **Index Configuration**: Ensure lookup indexes are defined by querying:
  ```sql
  SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';
  ```
  Ensure `idx_users_email`, `idx_products_sku`, `idx_inventory_product_id`, `idx_transactions_product_id`, `idx_forecasts_product_id_date` are present.

---

## ⚡ 2. Automated Inventory Trigger Validation
To verify the automated trigger updates the inventory correctly:

1. Insert a dummy product:
   ```sql
   INSERT INTO products (sku, name, category, unit_price, reorder_level)
   VALUES ('PROD-TEST-01', 'Verification Test Box', 'Logistics', 15.00, 5)
   RETURNING id;
   ```
2. Note the returned `product_id`.
3. Check `inventory` (should either be empty or initialized with `0` stock depending on transaction state).
4. Perform an **INBOUND** transaction:
   ```sql
   INSERT INTO transactions (product_id, quantity, transaction_type, reference_note)
   VALUES ('[YOUR-PRODUCT-ID]', 100, 'INBOUND', 'First import batch');
   ```
5. Query the inventory table:
   ```sql
   SELECT stock_on_hand FROM inventory WHERE product_id = '[YOUR-PRODUCT-ID]';
   ```
   *Expected Outcome*: `stock_on_hand` equals **100**.
6. Perform an **OUTBOUND** transaction:
   ```sql
   INSERT INTO transactions (product_id, quantity, transaction_type, reference_note)
   VALUES ('[YOUR-PRODUCT-ID]', 30, 'OUTBOUND', 'Customer shipment');
   ```
7. Query the inventory table:
   ```sql
   SELECT stock_on_hand FROM inventory WHERE product_id = '[YOUR-PRODUCT-ID]';
   ```
   *Expected Outcome*: `stock_on_hand` decreased by 30, now equals **70**.
8. Test bounds integrity: Insert an outbound transaction for quantity `150` (which exceeds hand stock).
   *Expected Outcome*: `stock_on_hand` stays at `0` due to `GREATEST(0, ...)` constraint instead of falling negative.

---

## 🔒 3. Environmental Security Audit
- [ ] Ensure that `.env` is created locally under `backend/` and populated with live Supabase URLs and keys.
- [ ] Run `git status` to verify that `.env` is omitted from Git staging (this is handled by our `.gitignore`).
- [ ] Ensure `backend/.env.example` remains updated with mock placeholders.

---

## 🔌 4. API Endpoints Handshake Check
- [ ] Start the FastAPI server:
  ```bash
  cd backend
  uvicorn main:app --reload
  ```
- [ ] Query the live validation endpoint: `GET http://127.0.0.1:8000/api/v1/health-check`.
  - **Success Case (DB Connected)**: Status Code `200 OK`
    ```json
    {
      "status": "healthy",
      "database": "connected",
      "validation": "success",
      "message": "OpsMind AI database connection is fully active."
    }
    ```
  - **Failure Case (Incorrect connection params or database downtime)**: Status Code `503 Service Unavailable`
    ```json
    {
      "detail": {
        "status": "unhealthy",
        "database": "disconnected",
        "message": "Connection to the Supabase instance could not be established.",
        "details": "[Traceback details here...]"
      }
    }
    ```
