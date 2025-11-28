import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

# Load train and test data
train_path = '../../artifacts/transformed_train_data.csv'
test_path = '../../artifacts/transformed_test_data.csv'
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# Features and labels
X_train = train_df['review_text']
y_train = train_df['sentiment_label']
X_test = test_df['review_text']
y_test = test_df['sentiment_label']

# Vectorize text
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Models to train
def train_and_evaluate(model, name):
    model.fit(X_train_vec, y_train)
    preds = model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    print(f'\n{name} Accuracy: {acc:.4f}')
    print(classification_report(y_test, preds))

models = [
    (LogisticRegression(max_iter=1000), 'Logistic Regression'),
    (RandomForestClassifier(n_estimators=100), 'Random Forest'),
    (SVC(), 'Support Vector Machine'),
]

for model, name in models:
    train_and_evaluate(model, name)
