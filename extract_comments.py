import argparse
import logging

from pathlib import Path

import pandas as pd

from core.Article import Article


# Path to the spreadsheet
SPREADSHEET_PATH = Path("data/raw/Articles for Opinion Mining 17.4.23.xlsx")
SPREADSHEET_SHEETS = {
    'bbc': 'BBC Only',
    'guardian': 'Guardian Only',
    'dailymail': 'Mail Online Only'
}


def load_articles_from_spreadsheet(spreadsheet_path, TARGET_SHEET_NAME):
    """
    Loads articles from the spreadsheet into memory
    """
    articles = []
    df = pd.read_excel(spreadsheet_path, sheet_name=TARGET_SHEET_NAME)
    
    for index, row in df.iterrows():
        articles.append(Article(row['Article Number'],
                                row['Headline'],
                                row['Date'],
                                row['Outlet'],
                                row['Article URL']
                                ))
        
    return articles


if __name__ == "__main__":
    # Get the Article ID to extract comments from
    parser = argparse.ArgumentParser(description="Extract comments from an Article ID.")
    parser.add_argument("outlet", type=str, help="The name of the news outlet to extract from")
    parser.add_argument("article_id", type=int, help="The Article ID of the article to extract comments from")
    args = parser.parse_args()

    target_article_id = args.article_id
    TARGET_SHEET_NAME = SPREADSHEET_SHEETS[args.outlet]


    # Setup logging
    logging.basicConfig(format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


    # Load articles
    logging.info("Loading articles from sheet %s from %s" % (TARGET_SHEET_NAME, SPREADSHEET_PATH))
    
    articles = load_articles_from_spreadsheet(SPREADSHEET_PATH, TARGET_SHEET_NAME)
    
    logging.info("Loaded all articles from sheet %s from %s" % (TARGET_SHEET_NAME, SPREADSHEET_PATH))


    # Process articles
    logging.info("Processing articles")
    
    for article in articles:
        if article.article_id == target_article_id:
            logging.info("Found target article %s" % target_article_id)
            article.extract_comments()
            article.save_comments_to_csv(folder=args.outlet)
    
    logging.info("Processed articles")