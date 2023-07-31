import logging
import sqlite3

from pathlib import Path

import pandas as pd


logging.basicConfig(format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

DATABASE_PATH = Path("data/processed/covid-blame.db")
SPREADSHEET_PATH = Path("data/raw/Articles for Opinion Mining 17.4.23.xlsx")

# Load database
logging.info("Connecting to database")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()


# Process each sheet in the articles spreadsheet
for sheet in ['BBC Only', 'Guardian Only', 'Mail Online Only']:
    logging.info(f"Inserting articles from {sheet} to database")
    df = pd.read_excel(SPREADSHEET_PATH, sheet_name=sheet)

    for _, row in df.iterrows():
        # Extract each column from the article
        article_id = row['Article Number']
        headline = row['Headline']
        date = row['Date'].strftime('%Y-%m-%d')
        outlet = row['Outlet']
        wayback_url = row['Wayback URL']
        article_url = row['Article URL']
        domestic_or_foreign_news = row['Domestic or Foreign News']
        primary_topic = row['Primary Topic/Theme']
        secondary_topic = row['Secondary Topic/Theme']
        comment_or_opinion = row['Comment or Opinion']
        story_open_for_comments = row['Story open for Comments']
        twitter_comments = row['Twitter Comments']
        twitter_url = row['Twitter URL']
        facebook_comments = row['Facebook Comments']
        facebook_url = row['Facebook URL']
        additional_notes = row['Additional Notes']
        random_values = row['Random values']

        # Insert the article into the database
        cursor.execute('''INSERT INTO articles
                        (article_id, headline, date, outlet, wayback_url, article_url,
                        domestic_or_foreign_news, primary_topic, secondary_topic,
                        comment_or_opinion, story_open_for_comments, twitter_comments,
                        twitter_url, facebook_comments, facebook_url, additional_notes,
                        random_values)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (article_id, headline, date, outlet, wayback_url, article_url,
                        domestic_or_foreign_news, primary_topic, secondary_topic,
                        comment_or_opinion, story_open_for_comments, twitter_comments,
                        twitter_url, facebook_comments, facebook_url, additional_notes,
                        random_values))


# Save the changes to the file
conn.commit()
conn.close()
logging.info("Saved database")
