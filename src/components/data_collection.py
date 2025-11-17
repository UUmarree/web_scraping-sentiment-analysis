import os
import requests
import pandas as pd
from src.logger import logging
from src.exception import CustomException


class DataCollector:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.artifact_path = os.path.join("artifacts", "imdb_cleaned.csv")

    def collect_data(self):
        try:
            logging.info("Sending request to IMDB AJAX endpoint...")
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()

            

            # Extract reviews from JSON (IMDB GraphQL format)
            res = []
            data = response.json()
            for res in data['data']['title']['reviews']['edges']:
                res.append(res)

              
            df = pd.json_normalize(res)
            df.to_csv('imdb_reviews.csv', index=False)    

            # Make artifacts folder
            os.makedirs("artifacts", exist_ok=True)

            df.to_csv(self.artifact_path, index=False)

            logging.info(f"Scraped {len(df)} reviews and saved to → {self.artifact_path}")

            return self.artifact_path

        except Exception as e:
            raise CustomException(e)
