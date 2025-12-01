from src.exception import CustomException
from src.logger import logging
import sys
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
import psycopg2

@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join('artifacts', 'raw_data.csv')
    train_data_path: str = os.path.join('artifacts', 'train_data.csv')
    test_data_path: str = os.path.join('artifacts', 'test_data.csv')

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion...")

        try:
            # -------------------------------
            # 1. CONNECT TO POSTGRES
            # -------------------------------
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                database=os.getenv("POSTGRES_DB", "Review_Data"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", ""),
            )
            cursor = conn.cursor()

            # -------------------------------
            # 2. READ ALL REVIEWS FROM TABLE
            # -------------------------------
            query = "SELECT id, movie_id, movie_name, review_text FROM reviews;"
            cursor.execute(query)
            rows = cursor.fetchall()

            if len(rows) == 0:
                logging.warning("⚠ No data found in Postgres reviews table")
                return

            # -------------------------------
            # 3. CONVERT TO DATAFRAME
            # -------------------------------
            df = pd.DataFrame(rows, columns=["id","movie_id", "movie_name", "review_text"])
            logging.info(f"Fetched {len(df)} rows from Postgres")

            # -------------------------------
            # 4. SAVE RAW CSV
            # -------------------------------
            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path, index=False)
            logging.info("Saved raw data to CSV")

            # -------------------------------
            # 5. TRAIN-TEST SPLIT
            # -------------------------------
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)

            train_set.to_csv(self.ingestion_config.train_data_path, index=False)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False)

            logging.info("Saved train.csv and test.csv successfully")

            cursor.close()
            conn.close()

            return self.ingestion_config.train_data_path, self.ingestion_config.test_data_path

        except Exception as e:
         print("Error:", e)

if __name__ == "__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()
