# OpsMind AI - Phase 3 Verification Checklist & Ingestion Validation

This document outlines the detailed verification tests to execute after setting up the data pipeline and admin router components.

---

## 📁 1. Generated Raw File Verification
Run the standalone data generator script from the project root folder:
```bash
python dataset/generate_mock_data.py
```
After execution, verify the output flat file:
- [ ] **Path Integrity**: Confirm file exists at `dataset/raw/warehouse_sales_raw.csv`.
- [ ] **Structural Validation**: Open the CSV file and verify columns:
  - `date` (YYYY-MM-DD format)
  - `sku` (`SKU-001` through `SKU-005`)
  - `product_name`
  - `category`
  - `unit_price`
  - `reorder_level`
  - `quantity` (integers representing daily sales/replenishments)
  - `transaction_type` (`OUTBOUND` or `INBOUND`)
  - `is_promotion` (`0` or `1`)
- [ ] **Length Integrity**: Verify the file contains exactly `730 * 5` (3,650) sales transactions plus the inbound initial and periodic replenishment transactions (totaling ~3,700+ rows).

---

## 📡 2. Endpoint Verification
Start the FastAPI application and trigger the ingestion pipeline:
```bash
cd backend
uvicorn main:app --reload
```
Using an API client (like Postman or `curl`), execute a POST request:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/admin/ingest-data
```
Verify the payload response matches this telemetry pattern:
```json
{
  "status": "success",
  "total_products_loaded": 5,
  "total_transactions_recorded": 3762,
  "message": "Data pipeline executed, cleansed, and committed successfully."
}
```
*Note: The number of total transactions recorded will vary slightly based on the random seed and how many replenishment cycles were triggered, but it should be consistently above 3,700.*

---

## 🗄️ 3. Live Database Validation
Log in to your **Supabase dashboard** -> **SQL Editor** or run queries to verify pipeline and trigger accuracy:

### Product Catalog Check
Verify that products have been registered:
```sql
SELECT sku, name, category, unit_price, reorder_level FROM products;
```
*Expected Outcome*: Exactly 5 records with fields corresponding to our `generate_mock_data.py` metadata list.

### Historical Transactions Check
Verify the quantity of records in the transactions table:
```sql
SELECT count(*) FROM transactions;
```
*Expected Outcome*: Value matches the `total_transactions_recorded` telemetry count.

### Downstream Triggers & Real-Time Inventory Validation
Verify that the Phase 2 database trigger executed successfully and computed exact stock balances for the product profiles:
```sql
SELECT p.sku, i.stock_on_hand, p.reorder_level
FROM products p
JOIN inventory i ON i.product_id = p.id;
```
*Expected Outcome*:
- Each of the 5 SKUs must have a matching `stock_on_hand` record in `inventory`.
- The `stock_on_hand` must be a positive integer reflecting:
  $$\text{stock\_on\_hand} = \sum (\text{INBOUND quantity}) - \sum (\text{OUTBOUND quantity}) \ge 0$$
- This verifies that our **Phase 2 Trigger function** (`update_inventory_on_transaction()`) correctly intercepted the bulk-inserted rows from the Python SQLAlchemy transaction layer!
