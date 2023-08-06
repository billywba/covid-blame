import time
import logging

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class BBCCommentExtractor():
    def __init__(self):
        # Set Chrome options
        options = Options()
        # options.add_argument('--headless')

        # Launch Chrome
        self.driver = webdriver.Chrome(options=options)


    def extract_comments_from_original_article_url(self, original_article_url):
        """
        Main function to extract all of the comments
        """
        logging.info("Extracting comments for %s" % original_article_url)
        
        article_url = self._generate_comment_embed_url(original_article_url)
        
        # Create a pandas dataframe to store the comments
        comments_df = pd.DataFrame(columns=['comment_id', 'parent_comment_id', 'comment', 'author_city', 'author_country', 'likes', 'dislikes'])
        

        # Load the page and wait 5 seconds
        self.driver.get(article_url)
        time.sleep(5)
        logging.info("Loaded article (%s)" % article_url)
        

        # Print amount of comments
        self.TOTAL_COMMENTS = int(self.driver.find_element(By.CLASS_NAME, 'comments-total').text.split(" ")[0])
        logging.info("This article contains %s comments" % self.TOTAL_COMMENTS)


        self._load_all_comments()
        logging.info("Loaded all comments")

        
        self._load_all_replies()
        logging.info("Loaded all replies")


        # Extract comments
        comment_text_divs = self.driver.find_elements(By.CLASS_NAME, 'comment__text')
        comment_ratings_divs = self.driver.find_elements(By.CLASS_NAME, 'comment__ratings')
        comment_down_ratings_divs = self.driver.find_elements(By.CLASS_NAME, 'comment__down-ratings')
        
        logging.info("Comment text divs: %d" % len(comment_text_divs))
        logging.info("Comment ratings divs: %d" % len(comment_ratings_divs))
        logging.info("Comment down ratings divs: %d" % len(comment_down_ratings_divs))

        comment_id_index = 1
        parent_comment_id_index = 1

        for i in range(0, len(comment_text_divs)):
            comment_text_div = comment_text_divs[i]
            comment_data = comment_text_div.text

            # Clean comments
            comment_data = comment_data.replace("\n\n", " ")
            comment_data = comment_data.replace("\n", " ")
            comment_data = comment_data.replace("<br><br>", " ")
            comment_data = comment_data.replace("<br>", " ")

            comment_likes_div = comment_ratings_divs[i]
            comment_dislikes_div = comment_down_ratings_divs[i]

            comment_likes = comment_likes_div.find_elements(By.CLASS_NAME, 'comment-rating__button-number')[0].text
            comment_dislikes = comment_dislikes_div.find_elements(By.CLASS_NAME, 'comment-rating__button-number')[0].text

            extracted_comment = {
                                    "comment_id": comment_id_index, 
                                    "parent_comment_id": parent_comment_id_index if self._is_comment_a_reply(comment_text_div) else "", 
                                    "comment": comment_data, 
                                    "likes": comment_likes, 
                                    "dislikes": comment_dislikes
                                }
            
            comments_df = pd.concat([comments_df, pd.DataFrame([extracted_comment])], ignore_index=True)

            # Increase ID's
            if not self._is_comment_a_reply(comment_text_div):
                parent_comment_id_index = comment_id_index

            comment_id_index += 1

        logging.info("Extracted %d/%d comments from %s" % (len(comments_df), self.TOTAL_COMMENTS, article_url))

        return comments_df
        
        
    def _load_all_comments(self):
        # Continue clicking next comments button until at bottom of the page
        while comment_button := self.driver.find_elements(By.CLASS_NAME, 'comments-button'):
            loaded_comments_count = len(self.driver.find_elements(By.CLASS_NAME, "comment__text"))
            logging.info("Loading more comments (%s/%s)" % (loaded_comments_count, self.TOTAL_COMMENTS))
            comment_button[0].click()
            time.sleep(10)


    def _load_all_replies(self):
        # Load all replies to comments
        while replies_button := self.driver.find_elements(By.CLASS_NAME, 'reply-more-replies__text'):
            logging.info("Loading more replies (%d remain)" % len(replies_button))
            loaded_comments_count = len(self.driver.find_elements(By.CLASS_NAME, "comment__text"))
            logging.info("Loading more replies (%s/%s)" % (loaded_comments_count, self.TOTAL_COMMENTS))
            replies_button[0].click()
            time.sleep(3)


    def _is_comment_a_reply(self, comment_text_element):
        parent = comment_text_element.find_element(By.XPATH, "../../../../../../../..").get_attribute('class')
        return parent == "replies"


    def _generate_comment_embed_url(self, original_article_url):
        """
        The original BBC article requires the user to click a view comments button. This button 
        creates a HTTP GET request to https://www.bbc.co.uk/comments/embed/news/ which is where the
        comments are actually stored.
        """
        bbc_article_id = original_article_url.split("/")[-1]
        return "https://www.bbc.co.uk/comments/embed/news/" + bbc_article_id
