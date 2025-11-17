import psycopg2

# Connect to your Postgres database
conn = psycopg2.connect(
    host="localhost",       # usually localhost if running locally
    database="Review_Data", # your database name
    user="postgres",        # your Postgres username
    password="Hideonbush12!" # your password
)

cur = conn.cursor()  # create a cursor to execute SQL commands

# Test the connection
cur.execute("SELECT version();")
print(cur.fetchone())  # prints PostgreSQL version

cur.close()
conn.close()
