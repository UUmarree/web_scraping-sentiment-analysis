from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from src.components.data_transformation import (
    analyze_sentiment_vader,
    clean_text_pipeline,
    get_sentiment_label,
)


@dataclass
class PredictionSummary:
    total: int
    positive: int
    neutral: int
    negative: int

    @property
    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "positive": self.positive,
            "neutral": self.neutral,
            "negative": self.negative,
        }


def _ensure_text_column(df: pd.DataFrame, text_column: str) -> None:
    if text_column not in df.columns:
        raise ValueError(
            f"Column '{text_column}' not found in dataset. "
            f"Columns available: {', '.join(df.columns)}"
        )


def _clean_reviews(df: pd.DataFrame, text_column: str) -> pd.Series:
    return (
        df[text_column]
        .astype(str)
        .fillna("")
        .apply(lambda text: clean_text_pipeline(text, keep_simple_html=False))
    )


def _extract_sentiment(cleaned_text: pd.Series) -> pd.DataFrame:
    scores = cleaned_text.apply(analyze_sentiment_vader)
    sentiment_df = pd.DataFrame(scores.tolist(), index=cleaned_text.index)
    sentiment_df["sentiment_label"] = sentiment_df["compound"].apply(get_sentiment_label)
    return sentiment_df.rename(
        columns={
            "compound": "sentiment_compound",
            "pos": "sentiment_pos",
            "neu": "sentiment_neu",
            "neg": "sentiment_neg",
        }
    )


def predict_from_dataframe(
    df: pd.DataFrame, text_column: str = "review_text"
) -> pd.DataFrame:
    """Return dataframe enriched with cleaned text + sentiment scores."""
    if df.empty:
        raise ValueError("Received an empty dataframe. Provide at least one row to score.")

    _ensure_text_column(df, text_column)
    result = df.copy()
    result["cleaned_text"] = _clean_reviews(result, text_column)
    sentiment = _extract_sentiment(result["cleaned_text"])
    return pd.concat([result, sentiment], axis=1)


def predict_from_csv(
    csv_path: Path | str,
    text_column: str = "review_text",
) -> pd.DataFrame:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find CSV at {csv_path}")

    df = pd.read_csv(csv_path)
    return predict_from_dataframe(df, text_column=text_column)


def summarize_predictions(df: pd.DataFrame) -> PredictionSummary:
    counts = df["sentiment_label"].value_counts()
    return PredictionSummary(
        total=len(df),
        positive=int(counts.get("positive", 0)),
        neutral=int(counts.get("neutral", 0)),
        negative=int(counts.get("negative", 0)),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run sentiment predictions on a CSV file.")
    parser.add_argument("csv_path", type=str, help="Path to CSV containing a review_text column.")
    parser.add_argument(
        "--text-column",
        default="review_text",
        help="Column name that contains the free-text reviews.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to write predictions as CSV.",
    )

    args = parser.parse_args()
    predictions = predict_from_csv(args.csv_path, text_column=args.text_column)
    summary = summarize_predictions(predictions)
    print("Prediction summary:", summary.as_dict)

    if args.output:
        output_path = Path(args.output)
        predictions.to_csv(output_path, index=False)
        print(f"Wrote predictions to {output_path.resolve()}")
