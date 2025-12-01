import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

# Load train and test data
train_path = '../../artifacts/transformed_train_data.csv'
test_path = '../../artifacts/transformed_test_data.csv'
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# Features and labels (explicitly select feature column to avoid label leakage)
feature_col = 'review_text'
label_col = 'sentiment_label'

# Ensure we only use the text column as features (no leakage)
if feature_col not in train_df.columns or feature_col not in test_df.columns:
    raise ValueError(f"Feature column '{feature_col}' not found in train/test data")
if label_col not in train_df.columns or label_col not in test_df.columns:
    raise ValueError(f"Label column '{label_col}' not found in train/test data")

X_train = train_df[feature_col].astype(str).copy()
y_train = train_df[label_col].astype(str).copy()
X_test = test_df[feature_col].astype(str).copy()
y_test = test_df[label_col].astype(str).copy()

print(f"Using feature column: {feature_col}. Label column: {label_col} (will not be used as a feature)")

# Vectorize text
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Models to train
def train_and_evaluate(model, name):
    model.fit(X_train_vec, y_train)
    preds = model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    print(f'\n{"="*60}')
    print(f'{name} Accuracy: {acc:.4f}')
    print(f'{"="*60}')
    print(classification_report(y_test, preds, zero_division=0))
    print(f'Confusion Matrix:\n{confusion_matrix(y_test, preds)}')

models = [
    (LogisticRegression(max_iter=1600), 'Logistic Regression'),
    (RandomForestClassifier(n_estimators=120), 'Random Forest'),
    (SVC(), 'Support Vector Machine'),
]

for model, name in models:
    train_and_evaluate(model, name)
