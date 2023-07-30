import sqlite3
from pathlib import Path


# Create database path and create directory if it doesn't exist
DATABASE_PATH = Path("./data/processed/covid-blame.db")
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create the SQLite file
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

    # Create comments table
    cursor.execute('''
                    CREATE TABLE comments
                    (
                        comment_id INTEGER PRIMARY KEY,
                        article_id INTEGER,
                        parent_comment_id INTEGER,
                        comment TEXT,
                        author_city TEXT,
                        author_country TEXT,
                        likes INTEGER,
                        dislikes INTEGER,
                        source TEXT,
                        FOREIGN KEY (article_id) REFERENCES articles (article_id)
                    )
                ''')
except sqlite3.OperationalError as e:
    print(f"Error: {e}") 

# Save the changes to the file
conn.commit()
conn.close()
