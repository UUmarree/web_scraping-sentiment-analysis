from bs4 import BeautifulSoup
import requests
import os
from src.exception import CustomException
from src.logger import logging
import sys
import pandas as pd
from sklearn.model_selection import train_test_split    
from dataclasses import dataclass
### Data Ingestion Component
### knows where to save each of the data artifacts
@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join('artifacts', 'raw_data.csv')
    train_data_path: str = os.path.join('artifacts', 'train_data.csv')
    test_data_path: str = os.path.join('artifacts', 'test_data.csv')

### Data Ingestion Class 
### Responsible for data ingestion
class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
        
    
    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion process")
        try:
            df = pd.read_csv('') ### later for after doing web scraping
            logging.info("Data read successfully from source")
            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path, index=False)
            logging.info("Raw data saved successfully")
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
            train_set.to_csv(self.ingestion_config.train_data_path, index=False)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False)
            logging.info("Train and test data saved successfully")

        except:
            pass

if __name__=="__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()            # Create artifacts directory if it doesn't exist