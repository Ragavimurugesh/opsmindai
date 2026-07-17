'''Kaggle dataset ingestion script.
- Uses kaggle CLI to download the Kaggle demand forecasting dataset (train.csv).
- Loads the CSV into a Pandas DataFrame, applies preprocessing from utils.preprocess.
- Inserts cleaned records into Supabase/PostgreSQL via the bulk ingestion service.
'''
import os
import subprocess
import pandas as pd
from pathlib import Path

# Adjust these constants as needed
KAGGLE_COMPETITION = "demand-forecasting-kernels-only"
TRAIN_CSV = "train.csv"
DATA_DIR = Path(__file__).parent / "data"

def download_dataset():
    """Download the Kaggle competition dataset using the kaggle CLI.
    Requires the user to have a valid Kaggle API token at ~/.kaggle/kaggle.json.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Use subprocess to call kaggle API; ensure it's installed in the environment.
    cmd = ["kaggle", "competitions", "download", KAGGLE_COMPETITION, "-p", str(DATA_DIR), "-f", TRAIN_CSV]
    subprocess.run(cmd, check=True)
    # Extract the zip if needed (kaggle CLI may deliver a zip archive)
    zip_path = DATA_DIR / f"{KAGGLE_COMPETITION}.zip"
    if zip_path.exists():
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(DATA_DIR)
        zip_path.unlink()

def load_and_preprocess() -> pd.DataFrame:
    """Load the downloaded CSV and run the shared preprocessing pipeline.
    Returns a cleaned DataFrame ready for DB insertion.
    """
    csv_path = DATA_DIR / TRAIN_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"{TRAIN_CSV} not found after download."
                               )
    df = pd.read_csv(csv_path)
    # The project already includes a generic preprocessing module.
    from utils.preprocess import preprocess_dataframe
    cleaned = preprocess_dataframe(df)
    return cleaned

def ingest_to_db(db_session):
    """Insert the preprocessed data into the database using the bulk ingestion service.
    The service expects a list of mapping dicts matching the Transaction model schema.
    """
    from services.ingestion import bulk_insert_transactions
    df = load_and_preprocess()
    # Convert DataFrame rows to list of dicts aligned with Transaction columns.
    records = df.to_dict(orient="records")
    bulk_insert_transactions(db_session, records)

def main():
    """Entry point for command‑line execution.
    This function can be invoked directly via `python -m backend.dataset.ingest_kaggle_data`.
    """
    from database import SessionLocal
    download_dataset()
    with SessionLocal() as db:
        ingest_to_db(db)
    print("Kaggle dataset successfully ingested.")

if __name__ == "__main__":
    main()
