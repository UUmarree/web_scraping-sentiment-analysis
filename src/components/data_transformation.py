import src.logger
from src.logger import logging
logging.info("Logger test: data_transformation.py script started")
import sys
import os
import re
import unicodedata
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
from nltk.sentiment import SentimentIntensityAnalyzer
from src.exception import CustomException

# Base directory: repository root (two levels up from this file)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Ensure VADER lexicon is available
import nltk
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
@dataclass
class DataTransformationConfig:
    transformed_train_path: str = os.path.join(BASE_DIR, 'artifacts', 'transformed_train_data.csv')
    transformed_test_path: str = os.path.join(BASE_DIR, 'artifacts', 'transformed_test_data.csv')
    transformed_data_path: str = os.path.join(BASE_DIR, 'artifacts', 'transformed_data.csv')
    test_size: float = 0.2


def _normalize_unicode(text: str) -> str:
    if not isinstance(text, str):
        return text
    return unicodedata.normalize("NFKC", text)


def _remove_control_chars(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r"[\x00-\x1F\x7F]+", "", text)


def _reduce_repeated_chars(text: str) -> str:
    # Reduce very long repeated characters (loooool -> loool or lol depending on rule)
    if not isinstance(text, str):
        return text
    return re.sub(r"(.)\1{2,}", r"\1\1", text)


def _remove_urls(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def sanitize_keep_tags(html: str, allowed_tags=None) -> str:
    """Return HTML that only contains a small set of allowed tags and no attributes.

    - Unwraps disallowed tags (keeps their text) and strips attributes from allowed tags.
    - Uses BeautifulSoup which is already installed in your environment.
    """
    if not isinstance(html, str):
        return html
    if allowed_tags is None:
        allowed_tags = ["p", "br", "b", "i", "strong", "em", "ul", "ol", "li", "a"]
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            # remove all attributes to keep tags simple
            tag.attrs = {}
    # Return string representation (will include simple tags) but strip leading/trailing whitespace
    return str(soup).strip()


def html_to_simple_text(html: str) -> str:
    """Convert HTML to plain/simple text while preserving basic whitespace and simple newlines.
    This is useful when you want plain text (no tags).
    """
    if not isinstance(html, str):
        return html
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    return text


def clean_text_pipeline(text: str, keep_simple_html: bool = False, allowed_tags=None) -> str:
    """Full cleaning pipeline:
    - Optionally keep only a small set of HTML tags (no attributes)
    - Normalize unicode
    - Remove URLs
    - Remove control chars
    - Reduce repeated characters
    - Collapse whitespace
    """
    if not isinstance(text, str):
        return text
    if keep_simple_html:
        text = sanitize_keep_tags(text, allowed_tags=allowed_tags)
    else:
        text = html_to_simple_text(text)
    text = _normalize_unicode(text)
    text = _remove_urls(text)
    text = _remove_control_chars(text)
    text = _reduce_repeated_chars(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_sentiment_vader(text: str) -> dict:
    """Analyze sentiment using VADER (Valence Aware Dictionary and sEntiment Reasoner).
    
    VADER is optimized for social media text and returns:
    - 'compound': normalized composite score [-1 (most negative) to +1 (most positive)]
    - 'pos': proportion of positive words
    - 'neu': proportion of neutral words
    - 'neg': proportion of negative words
    
    Returns a dict with keys: compound, pos, neu, neg
    """
    if not isinstance(text, str) or not text.strip():
        return {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}
    
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    return scores


def get_sentiment_label(compound_score: float) -> str:
    """Convert VADER compound score to a sentiment label.
    
    - compound >= 0.05: positive
    - compound <= -0.05: negative
    - otherwise: neutral
    """
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'


class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()

    def initiate_data_transformation(self):
        logging.info("Starting data transformation...")

        try:
            # -------------------------------
            # 1. READ RAW DATA
            # -------------------------------
            raw_data_path = os.path.join(BASE_DIR, 'src', 'components', 'artifacts', 'raw_data.csv')
            df = pd.read_csv(raw_data_path)
            logging.info(f"Read raw data from {raw_data_path} with shape {df.shape}")
            # -------------------------------
            # 2. DATA CLEANING
            # Example cleaning: Drop duplicates and handle missing values
            df.drop_duplicates(subset=['review_text'], inplace=True)
            df.dropna(subset=['review_text'], inplace=True)

            # Apply text cleaning pipeline - convert HTML to simple text and apply normalization
            # If you want to preserve a small set of HTML tags, set keep_simple_html=True
            df['review_text'] = df['review_text'].apply(lambda x: clean_text_pipeline(x, keep_simple_html=False))

            logging.info(f"Data after cleaning has shape {df.shape}")
            # -------------------------------
            # 2.5 SENTIMENT ANALYSIS WITH VADER
            # Analyze sentiment for each cleaned review
            logging.info("Performing VADER sentiment analysis...")
            sentiment_scores = df['review_text'].apply(analyze_sentiment_vader)
            df['sentiment_compound'] = sentiment_scores.apply(lambda x: x['compound'])
            df['sentiment_pos'] = sentiment_scores.apply(lambda x: x['pos'])
            df['sentiment_neu'] = sentiment_scores.apply(lambda x: x['neu'])
            df['sentiment_neg'] = sentiment_scores.apply(lambda x: x['neg'])
            df['sentiment_label'] = df['sentiment_compound'].apply(get_sentiment_label)
            logging.info(f"Sentiment analysis complete. Added columns: sentiment_compound, sentiment_pos, sentiment_neu, sentiment_neg, sentiment_label")
            # -------------------------------
            # 3. SAVE TRANSFORMED DATA
            os.makedirs(os.path.dirname(self.transformation_config.transformed_data_path), exist_ok=True)
            df.to_csv(self.transformation_config.transformed_data_path, index=False)
            logging.info(f"Saved transformed data to {self.transformation_config.transformed_data_path}")

            # -------------------------------

            # 4. SPLIT INTO TRAIN AND TEST SETS
            train_df, test_df = train_test_split(
                df, test_size=self.transformation_config.test_size, random_state=42
            )
            train_df.to_csv(self.transformation_config.transformed_train_path, index=False)
            test_df.to_csv(self.transformation_config.transformed_test_path, index=False)
            logging.info(f"Saved training data to {self.transformation_config.transformed_train_path} with shape {train_df.shape}")
            logging.info(f"Saved testing data to {self.transformation_config.transformed_test_path} with shape {test_df.shape}")
        except Exception as e:
            logging.error("Error during data transformation")
            raise CustomException(e, sys)
        return self.transformation_config.transformed_data_path

if __name__ == '__main__':
    DataTransformation().initiate_data_transformation()


