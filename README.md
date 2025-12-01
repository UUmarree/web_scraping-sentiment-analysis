## Web Scraping + Sentiment Analysis (IMDB Reviews)

End-to-end project that:

- **Scrapes IMDB reviews** into a Postgres database.
- **Ingests and cleans the text**, including HTML stripping and normalization.
- **Runs VADER sentiment analysis** to assign `positive`, `neutral`, or `negative` labels.
- Provides a **Streamlit frontend** to:
  - Analyze a **single review**.
  - Upload a **CSV dataset** and get instant sentiment predictions and a downloadable file.

The repo also includes an experimental **model training script** that benchmarks traditional ML models (Logistic Regression, Random Forest, SVM) on the transformed data, separate from the VADER-based production pipeline.

---

### Project structure (high level)

- `src/components/data_collection.py`  
  Scrapes IMDB reviews via the GraphQL API and stores them into a Postgres `reviews` table.

- `src/components/data_ingestion.py`  
  Reads all rows from Postgres `reviews`, saves a raw CSV, and creates a simple train/test split CSV.

- `src/components/data_transformation.py`  
  - Cleans the HTML review text (BeautifulSoup + regex).
  - Normalizes and sanitizes strings.
  - Runs **VADER** sentiment analysis (`nltk.sentiment.vader`) on each review.
  - Produces:
    - `artifacts/transformed_data.csv`
    - `artifacts/transformed_train_data.csv`
    - `artifacts/transformed_test_data.csv`

- `src/components/model_trainer.py`  
  Loads the transformed train/test CSVs and trains/evaluates:
  - Logistic Regression  
  - Random Forest  
  - Support Vector Machine  
  This is for experimentation / benchmarking only and is **not** currently wired into the frontend.

- `src/pipeline/predict_pipeline.py`  
  - Reuses the cleaning + VADER logic from `data_transformation`.
  - Provides helper functions:
    - `predict_from_dataframe(df, text_column="review_text")`
    - `predict_from_csv(csv_path, text_column="review_text")`
    - `summarize_predictions(df)` → counts of positive/neutral/negative.
  - Can be used as a CLI script for batch scoring a CSV.

- `frontend/app.py`  
  Streamlit app that:
  - Lets you test sentiment on a **single review** (text/HTML).
  - Lets you upload a **CSV** (choose which column holds the review text).
  - Uses `predict_from_dataframe` to generate VADER-based sentiment predictions.
  - Shows summary metrics and lets you download the predictions as CSV.

- `data/sample_reviews.csv`  
  Small sample dataset with a `review_text` column, useful for testing the Streamlit app without setting up Postgres or scraping IMDB.

- `test_sentiment.py`  
  Demo script that shows how the cleaning + VADER pipeline behaves on a list of hardcoded example reviews.

---

### VADER vs ML models (how predictions work)

**Main production predictions (used by the frontend)**  
The **Streamlit app and `predict_pipeline` use VADER** (a rule-based sentiment analyzer from NLTK).  
Pipeline:

1. Clean the raw review text (strip HTML, normalize, remove URLs, etc.).
2. Run VADER to get:
   - `sentiment_compound`
   - `sentiment_pos`, `sentiment_neu`, `sentiment_neg`
3. Map `sentiment_compound` to a label:
   - \(\ge 0.05 \Rightarrow\) `positive`
   - \(\le -0.05 \Rightarrow\) `negative`
   - otherwise `neutral`

These labels are what you see in the frontend predictions.

**Experimental ML models (offline only)**  
`src/components/model_trainer.py` is for **benchmarking** more traditional ML models:

1. Loads `artifacts/transformed_train_data.csv` and `artifacts/transformed_test_data.csv`.
2. Uses TF-IDF (`TfidfVectorizer`) on the `review_text` column.
3. Trains and evaluates Logistic Regression, Random Forest, and SVM.

Currently, these models are **not persisted or used** by the frontend app. If you want, you can extend the project by:

- Saving the best model with `joblib` or `pickle`.
- Loading it in `predict_pipeline.py`.
- Switching the frontend to call your trained model instead of VADER.

---

### Setup

#### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>.git
cd "Web Scraping + Sentiment Analysis"

python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Download the VADER lexicon (one-time)

```bash
python -m nltk.downloader vader_lexicon
```

#### 4. Configure Postgres credentials (for scraping / ingestion)

The code reads database settings from **environment variables**:

- `POSTGRES_HOST` (default: `localhost`)
- `POSTGRES_DB` (default: `Review_Data`)
- `POSTGRES_USER` (default: `postgres`)
- `POSTGRES_PASSWORD` (**no default**; must be set if your DB requires a password)

On Windows PowerShell, for example:

```powershell
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_DB="Review_Data"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="your_password_here"
```

You can set these in your system environment variables or in your shell before running the scripts.

---

### How to run each part

#### A. Use the Streamlit frontend (recommended for demos)

1. Make sure your virtualenv is activated and dependencies are installed.
2. Optionally, use the sample CSV:
   - `data/sample_reviews.csv` (has a `review_text` column).
3. Start the app:

```bash
streamlit run frontend/app.py
```

4. In the browser:
   - Try the **"Quick single-text check"** expander to analyze a single review.
   - Use **"Upload CSV file"** to:
     - Upload `data/sample_reviews.csv` (or your own CSV).
     - Select the column containing the review text (default is `review_text`).
     - Generate predictions, view summary metrics, and download the result as CSV.

#### B. Run the sentiment demo script

```bash
python test_sentiment.py
```

This will:

- Show how the text cleaning pipeline works.
- Run VADER on a set of hardcoded sentences.
- Print labels and some simple statistics.

#### C. Full pipeline from Postgres (optional, requires DB + IMDB credentials)

1. **Scrape IMDB reviews into Postgres**
   - Configure `urls.json` with a list of movies (`id`, `name`).
   - Make sure your Postgres DB is running and the `reviews` table exists.
   - Run:

   ```bash
   python -m src.components.data_collection
   ```

2. **Ingest from Postgres to CSVs**

   ```bash
   python -m src.components.data_ingestion
   ```

   This will create:

   - `artifacts/raw_data.csv`
   - `artifacts/train_data.csv`
   - `artifacts/test_data.csv`

3. **Transform data and run VADER sentiment**

   ```bash
   python -m src.components.data_transformation
   ```

   This will create:

   - `artifacts/transformed_data.csv`
   - `artifacts/transformed_train_data.csv`
   - `artifacts/transformed_test_data.csv`

4. **(Optional) Train ML models**

   ```bash
   python -m src.components.model_trainer
   ```

   You will see accuracy, classification reports, and confusion matrices for:

   - Logistic Regression
   - Random Forest
   - SVM

#### D. Batch predictions via CLI

You can use `predict_pipeline.py` directly on any CSV that has a text column:

```bash
python -m src.pipeline.predict_pipeline path\to\your.csv --text-column review_text --output predictions.csv
```

This runs the same cleaning + VADER logic as the frontend and writes a new CSV with:

- Cleaned text
- `sentiment_compound`, `sentiment_pos`, `sentiment_neu`, `sentiment_neg`
- `sentiment_label`

---

### Screenshots (optional but recommended)

For a polished GitHub presentation, add screenshots (e.g. in an `assets/` folder) and reference them here:

- Streamlit home screen
- Single-review analysis
- CSV upload + predictions table

Example (after you add the file):

```markdown
![Streamlit frontend](assets/frontend.png)
```

---

### License

This project is licensed under the terms of the **MIT License**.  
See the `LICENSE` file for details.

