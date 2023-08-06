import csv
import logging

from pathlib import Path

from core.BBCCommentExtractor import BBCCommentExtractor
from core.DailyMailCommentExtractor import DailyMailCommentExtractor
from core.GuardianCommentExtractor import GuardianCommentExtractor
from core.FacebookCommentExtractor import FacebookCommentExtractor


class Article:
    def __init__(self, article_id, headline, date, outlet, article_url, facebook_url):
        self.article_id = article_id
        self.headline = headline
        self.date = date
        self.outlet = outlet
        self.article_url = article_url
        self.facebook_url = facebook_url

        self.comments_df = {}


    def extract_comments(self):
        """
        Extract the comments from the article
        """
        comment_extractor = self.__get_comment_extractor()
        self.comments_df = comment_extractor.extract_comments_from_original_article_url(self.article_url)
    
    
    def extract_facebook_comments(self):
        """
        Extract the Facebook comments from the article
        """
        comment_extractor = FacebookCommentExtractor()
        self.comments_df = comment_extractor.extract_comments_from_post(self.facebook_url)


    def save_comments_to_csv(self, folder):
        """"
        Save the extracted comments to a .csv
        """
        # Create path to save .csv and ensure directory exists
        csv_file_directory = Path("data/external/comments/") / folder
        csv_file_directory.mkdir(parents=True, exist_ok=True)
        
        csv_file_path = csv_file_directory / f"{self.article_id}.csv"

        # Save the comments
        self.comments_df.to_csv(csv_file_path, index=False, quoting=csv.QUOTE_ALL, escapechar='\\')

        logging.info("Saved %s comments for %s to %s" % (len(self.comments_df), self.article_url, csv_file_path))


    def __get_comment_extractor(self):
        """
        Return the necessary comment extractor based on the Article URL
        """
        if "www.dailymail.co.uk" in self.article_url:
            return DailyMailCommentExtractor()
        elif "www.bbc.co.uk" in self.article_url or "www.bbc.com" in self.article_url:
            return BBCCommentExtractor()
        elif "www.theguardian.com" in self.article_url:
            return GuardianCommentExtractor()
