import logging
import sqlite3

from pathlib import Path


logging.basicConfig(format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

# Create database path and create directory if it doesn't exist
DATABASE_PATH = Path("data/processed/covid-blame.db")
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create the SQLite file
logging.info("Connecting to database")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # Create articles table
    cursor.execute('''
                    CREATE TABLE articles
                    (
                        article_id INTEGER PRIMARY KEY,
                        headline TEXT,
                        date TEXT,
                        outlet TEXT,
                        wayback_url TEXT,
                        article_url TEXT,
                        domestic_or_foreign_news INTEGER,
                        primary_topic INTEGER,
                        secondary_topic INTEGER,
                        comment_or_opinion BOOLEAN,
                        story_open_for_comments BOOLEAN,
                        twitter_comments INTEGER,
                        twitter_url TEXT,
                        facebook_comments INTEGER,
                        facebook_url TEXT,
                        additional_notes TEXT,
                        random_values INTEGER
                    )
                ''')
    logging.info("Created articles table")

    # Create comments table
    cursor.execute('''
                    CREATE TABLE comments
                    (
                        comment_id INTEGER PRIMARY KEY,
                        parent_comment_id INTEGER,
                        article_id INTEGER,
                        comment TEXT,
                        author_city TEXT,
                        author_country TEXT,
                        likes INTEGER,
                        dislikes INTEGER,
                        source TEXT,
                        FOREIGN KEY (article_id) REFERENCES articles (article_id)
                    )
                ''')
    logging.info("Created comments table")

except sqlite3.OperationalError as e:
    logging.error(f"Error: {e}") 

# Save the changes to the file
conn.commit()
conn.close()
logging.info("Saved database")
