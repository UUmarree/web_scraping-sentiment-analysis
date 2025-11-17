import requests
import psycopg2
import json
import time

class DataCollector:
    def __init__(self, db_config):
        try:
            self.conn = psycopg2.connect(**db_config)
            self.cur = self.conn.cursor()
            print("Connected to Postgres successfully!")
        except Exception as e:
            print("Failed to connect to Postgres:", e)
            raise

    def scrape_and_store(self, movie_id, movie_name, headers, first=25):
        base_url = "https://caching.graphql.imdb.com/"
        after_cursor = None
        total_inserted = 0

        while True:
            variables = {
                "after": after_cursor,
                "const": movie_id,
                "first": first,
                "locale": "en-US",
                "sort": {"by": "HELPFULNESS_SCORE", "order": "DESC"},
                "filter": {}
            }

            extensions = {
                "persistedQuery": {
                    "sha256Hash": "d389bc70c27f09c00b663705f0112254e8a7c75cde1cfd30e63a2d98c1080c87",
                    "version": 1
                }
            }

            payload = {
                "operationName": "TitleReviewsRefine",
                "variables": variables,
                "extensions": extensions
            }

            try:
                r = requests.post(base_url, headers=headers, json=payload, timeout=30)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                print(f"Failed to fetch data for {movie_name}: {e}")
                break

            # Access reviews
            reviews_section = data.get("data", {}).get("title", {}).get("reviews", {})
            edges = reviews_section.get("edges", [])
            page_info = reviews_section.get("pageInfo", {})

            if not edges:
                print(f"No more reviews found for {movie_name}")
                break

            # Insert into Postgres
            inserted_this_batch = 0
            for e in edges:
                node = e.get("node", {})
                review_text = node.get("text", {}).get("originalText", {}).get("plaidHtml", "")
                if review_text.strip():
                    try:
                        self.cur.execute(
                            """
                            INSERT INTO reviews (movie_id, movie_name, review_text)
                            VALUES (%s, %s, %s)
                            """,
                            (movie_id, movie_name, review_text)
                        )
                        inserted_this_batch += 1
                    except Exception as ex:
                        print("Insert failed:", ex)

            self.conn.commit()
            total_inserted += inserted_this_batch
            print(f"Inserted {inserted_this_batch} reviews for {movie_name} in this batch.")

            # Update cursor for next page
            after_cursor = page_info.get("endCursor")
            has_next = page_info.get("hasNextPage", False)
            if not has_next:
                break

            time.sleep(1)  # polite delay

        print(f"Total reviews inserted for {movie_name}: {total_inserted}")

    def close(self):
        self.cur.close()
        self.conn.close()
        print("Postgres connection closed.")


# ---------------- Main Script ----------------

db_config = {
    "host": "localhost",
    "database": "Review_Data",
    "user": "postgres",
    "password": "Hideonbush12!"  # Replace with your password
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "accept": "application/json",
    "content-type": "application/json"
}

# Load movies from url.json
with open("urls.json", "r") as f:
    config = json.load(f)

movies = config.get("movies", [])

if not movies:
    print("No movies found in url.json")
else:
    collector = DataCollector(db_config)
    for movie in movies:
        movie_id = movie.get("id")
        movie_name = movie.get("name")
        if movie_id and movie_name:
            collector.scrape_and_store(movie_id, movie_name, headers, first=25)
        else:
            print("Invalid movie entry in url.json:", movie)
    collector.close()
