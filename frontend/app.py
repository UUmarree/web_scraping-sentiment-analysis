from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.pipeline.predict_pipeline import (
    predict_from_dataframe,
    summarize_predictions,
)

st.set_page_config(
    page_title="IMDB Review Sentiment",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 IMDB Review Sentiment Explorer")
st.write(
    "Upload a CSV containing a `review_text` column (or pick another column) "
    "and instantly generate sentiment predictions using the VADER-powered pipeline."
)


def _display_summary(prediction_df: pd.DataFrame) -> None:
    summary = summarize_predictions(prediction_df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", summary.total)
    col2.metric("Positive", summary.positive)
    col3.metric("Neutral", summary.neutral)
    col4.metric("Negative", summary.negative)


with st.expander("Quick single-text check"):
    sample_text = st.text_area(
        "Enter a single review (plain text or HTML).",
        height=120,
        placeholder="Type or paste a review...",
    )
    if st.button("Analyze this review"):
        if not sample_text.strip():
            st.warning("Please provide some text before running the analysis.")
        else:
            df_single = pd.DataFrame({"review_text": [sample_text]})
            prediction = predict_from_dataframe(df_single)
            st.write("Prediction:", prediction["sentiment_label"].iloc[0].upper())
            st.json(prediction.iloc[0].to_dict())


uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        st.stop()

    if uploaded_df.empty:
        st.warning("Uploaded CSV is empty. Please upload a file with rows.")
        st.stop()

    st.success(f"Loaded dataset with shape {uploaded_df.shape}")
    candidate_columns = uploaded_df.columns.tolist()
    selected_column = st.selectbox(
        "Column that contains the review text:",
        options=candidate_columns,
        index=candidate_columns.index("review_text") if "review_text" in candidate_columns else 0,
    )

    if st.button("Generate predictions for dataset", type="primary"):
        with st.spinner("Running the sentiment pipeline..."):
            try:
                predictions = predict_from_dataframe(uploaded_df, text_column=selected_column)
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")
                st.stop()

        _display_summary(predictions)
        st.subheader("Preview (first 200 rows)")
        st.dataframe(predictions.head(200), use_container_width=True)

        buffer = io.StringIO()
        predictions.to_csv(buffer, index=False)
        st.download_button(
            label="Download predictions as CSV",
            data=buffer.getvalue(),
            file_name="sentiment_predictions.csv",
            mime="text/csv",
        )


else:
    st.info("Upload a CSV to unlock batch predictions.")

