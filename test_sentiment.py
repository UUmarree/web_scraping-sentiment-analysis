"""
Test script to demonstrate VADER sentiment analysis integration.
Run this to see sample sentiment analysis output.
"""

import pandas as pd
from src.components.data_transformation import (
    analyze_sentiment_vader,
    get_sentiment_label,
    clean_text_pipeline
)

# Sample review data (simulating what would come from raw_data.csv)
sample_reviews = [
    "This product is absolutely amazing! I love it so much!",
    "Terrible quality. Waste of money. Don't buy!",
    "It's okay. Nothing special but does the job.",
    "I'm extremely happy with this purchase!!! Highly recommend!!!",
    "Disgusting. Worst purchase ever. Never again.",
    "<p>Great product with <b>excellent</b> features!</p>",
    "https://example.com check this out. It's great!",
    "The service is good but the price is too high :(",
    "Love this! Best investment ever made.",
    "Not worth the hype. Very disappointed.",
    "Decent quality for the price point.",
    "Outstanding! Exceeded all my expectations!",
    "Poor workmanship. Broke after one week.",
    "Pretty good overall. Recommended!",
    "Absolutely terrible. Refunded immediately.",
    "It works as expected. Nothing more, nothing less.",
    "Fantastic product! Highly satisfied!",
    "Waste of money. Total garbage.",
    "Good value for money. Happy customer.",
    "Horrible experience. Will not buy again.",
]

print("=" * 80)
print("VADER SENTIMENT ANALYSIS DEMO")
print("=" * 80)
print()

# Create a sample dataframe
df = pd.DataFrame({
    'review_text': sample_reviews
})

print(f"Original Data (before cleaning):\n")
print(df[['review_text']].sample(min(8, len(df))))
print()

# Apply cleaning
print("Applying text cleaning pipeline...")
df['review_text_cleaned'] = df['review_text'].apply(
    lambda x: clean_text_pipeline(x, keep_simple_html=False)
)
print()

# Apply VADER sentiment analysis
print("Applying VADER sentiment analysis...")
sentiment_scores = df['review_text_cleaned'].apply(analyze_sentiment_vader)
df['sentiment_compound'] = sentiment_scores.apply(lambda x: x['compound'])
df['sentiment_pos'] = sentiment_scores.apply(lambda x: x['pos'])
df['sentiment_neu'] = sentiment_scores.apply(lambda x: x['neu'])
df['sentiment_neg'] = sentiment_scores.apply(lambda x: x['neg'])
df['sentiment_label'] = df['sentiment_compound'].apply(get_sentiment_label)
print()

# Display results
print("=" * 80)
print("RESULTS: Text Cleaning + VADER Sentiment Analysis")
print("=" * 80)
print()

for idx, row in df.iterrows():
    print(f"Sample {idx + 1}:")
    print(f"  Original:  {row['review_text'][:60]}...")
    print(f"  Cleaned:   {row['review_text_cleaned'][:60]}...")
    print(f"  Compound:  {row['sentiment_compound']:.4f}")
    print(f"  Positive:  {row['sentiment_pos']:.4f} | Neutral:  {row['sentiment_neu']:.4f} | Negative: {row['sentiment_neg']:.4f}")
    print(f"  Label:     {row['sentiment_label'].upper()}")
    print()

# Summary statistics
print("=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print()
print(f"Total samples: {len(df)}")
print(f"Positive sentiment: {(df['sentiment_label'] == 'positive').sum()} ({(df['sentiment_label'] == 'positive').sum()/len(df)*100:.1f}%)")
print(f"Neutral sentiment:  {(df['sentiment_label'] == 'neutral').sum()} ({(df['sentiment_label'] == 'neutral').sum()/len(df)*100:.1f}%)")
print(f"Negative sentiment: {(df['sentiment_label'] == 'negative').sum()} ({(df['sentiment_label'] == 'negative').sum()/len(df)*100:.1f}%)")
print()
print(f"Average compound score: {df['sentiment_compound'].mean():.4f}")
print(f"Std deviation:         {df['sentiment_compound'].std():.4f}")
print()
