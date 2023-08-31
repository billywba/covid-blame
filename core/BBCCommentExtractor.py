import csv
import requests
import time

import pandas as pd


class BBCCommentExtractor:
    def __init__(self):
        # Create a pandas dataframe to store the comments
        self.comments_df = pd.DataFrame(columns=['comment_id', 'parent_comment_id', 'comment', 'likes', 'dislikes'])

        # Track the comment_id and parent_comment_id of each comment
        self.comment_id_index = 1
        self.parent_comment_id_index = self.comment_id_index

        self.BBC_ARTICLE_ID = 0


    def extract_comments_from_original_article_url(self, article_url):
        url = self.__generate_starting_source_comment_url(article_url)

        while True:
            data = self.__fetch_comment_data(url)
            time.sleep(1)

            self.__process_comments(data['comments'])
            print(f"{len(self.comments_df)}")

            if data['canLoadMore']:
                next_token = data['nextToken']
                encoded_next_token = self.__encode_next_token(next_token)
                url = f"https://push.api.bbci.co.uk/proxy/data/bbc-morph-comments-data/apiKey/ecee5363-c17d-4257-8907-2cd0da83d26b/forumId/__CPS__{self.BBC_ARTICLE_ID}/isSortToggleOverrideOff/false/nextToken/{encoded_next_token}/pageSize/40/retry/1/sortOrder/HighestRated/version/4.8.0?timeout=5"
            else:
                break

        return self.comments_df


    def __process_comments(self, comments):
        for comment in comments:
            extracted_comment = {
                                    'comment_id': self.comment_id_index, 
                                    'parent_comment_id': "", 
                                    'comment': self.__clean_comment_text(comment['text']),
                                    'likes': comment['rating']['positive'], 
                                    'dislikes': comment['rating']['negative']
                                }

            # Add new comment to the dataframe
            self.comments_df = pd.concat([self.comments_df, pd.DataFrame([extracted_comment])], ignore_index=True)
            self.parent_comment_id_index = self.comment_id_index

            self.comment_id_index += 1

            if len(comment['replies']) > 0:
                self.__extract_replies(comment['id'])


    def __extract_replies(self, bbc_parent_comment_id):
        url = f"https://push.api.bbci.co.uk/proxy/data/bbc-morph-comments-data/apiKey/ecee5363-c17d-4257-8907-2cd0da83d26b/commentId/{bbc_parent_comment_id}/forumId/__CPS__{self.BBC_ARTICLE_ID}/pageSize/11/retry/1/startIndex/1/version/4.8.0?timeout=5"

        while True:
            data = self.__fetch_comment_data(url)
            time.sleep(1)

            if data is None:
                break

            self.__process_replies(data['replies'])

            if data['nextToken']:
                next_token = data['nextToken']
                encoded_next_token = self.__encode_next_token(next_token)
                url = f"https://push.api.bbci.co.uk/proxy/data/bbc-morph-comments-data/apiKey/ecee5363-c17d-4257-8907-2cd0da83d26b/commentId/{bbc_parent_comment_id}/forumId/__CPS__{self.BBC_ARTICLE_ID}/isSortToggleOverrideOff/false/nextToken/{encoded_next_token}/pageSize/40/retry/1/sortOrder/HighestRated/version/4.8.0?timeout=5"
            else:
                break

    
    def __process_replies(self, replies):
        for reply in replies:
            extracted_reply = {
                                    'comment_id': self.comment_id_index,
                                    'parent_comment_id': self.parent_comment_id_index,
                                    'comment': self.__clean_comment_text(reply['text']),
                                    'likes': reply['rating']['positive'], 
                                    'dislikes': reply['rating']['negative']
                                }
            
            # Add new comment to the dataframe
            self.comments_df = pd.concat([self.comments_df, pd.DataFrame([extracted_reply])], ignore_index=True)

            self.comment_id_index += 1


    def __clean_comment_text(self, comment_text):
        comment_text = comment_text.replace("<BR />", " ")
        return comment_text


    def __encode_next_token(self, token):
        encoded_next_token = token.replace("/", "%2F")
        encoded_next_token = encoded_next_token.replace("+", "%2B")
        encoded_next_token = encoded_next_token.replace("=", "%3D")

        return encoded_next_token


    def __fetch_comment_data(self, url):
        """
        Retrieves the raw comment data
        """
        response = requests.get(url)

        data = ""
        if response.status_code == 200:
            print("Received HTTP GET request (%s)" % url)
            data = response.json()
        else:
            print("Error extracting comments for %s" % url)

        return data   


    def __generate_starting_source_comment_url(self, original_article_url):
        bbc_article_id = original_article_url.split("-")[-1]
        self.BBC_ARTICLE_ID = bbc_article_id

        source_comment_url = f"https://push.api.bbci.co.uk/proxy/data/bbc-morph-comments-data/apiKey/ecee5363-c17d-4257-8907-2cd0da83d26b/forumId/__CPS__{bbc_article_id}/isSortToggleOverrideOff/false/pageSize/40/retry/1/sortOrder/HighestRated/version/4.8.0?timeout=5"
        
        return source_comment_url
