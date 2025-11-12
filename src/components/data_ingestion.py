from bs4 import BeautifulSoup
import requests
import os
from src.exception import CustomException
from src.logger import logging
import sys
import pandas as pd
from sklearn.model_selection import trian_test_split    
from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join('artifacts', 'raw_data.csv')
    train_data_path: str = os.path.join('artifacts', 'train_data.csv')
    test_data_path: str = os.path.join('artifacts', 'test_data.csv')


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
        

    def initiate_data_ingestion(self):
        logging.information("Starting data ingestion process")
        try:
            df = pd.read_csv('https://example.com/data.csv')
        except:
            pass