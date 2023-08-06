import requests
import logging

import pandas as pd

from bs4 import BeautifulSoup


class GuardianCommentExtractor:
    def extract_comments_from_original_article_url(self, original_article_url):
        """
        Main function to extract all of the comments
        """
        logging.info("Extracting comments for %s" % original_article_url)

        # Create a pandas dataframe to store the comments
        comments_df = pd.DataFrame(columns=['comment_id', 'parent_comment_id', 'comment', 'likes', 'dislikes'])

        # Track the comment_id and parent_comment_id of each comment
        comment_id_index = 1
        parent_comment_id_index = 1


        # Extract all comments
        total_pages = self.__get_total_amount_of_pages(original_article_url)
        for page in range(1, total_pages + 1):
            logging.info("Extracting page " + str(page))


            # Fetch the comments
            comment_data = self.__fetch_comment_data(original_article_url, page=page)


            # Process comments
            for comment in comment_data['discussion']['comments']:
                # Clean comment text
                comment_text = comment['body']
                soup = BeautifulSoup(comment_text, "html.parser")
                comment_text = soup.get_text()

                # Extract the data needed
                extracted_comment = {
                                        "comment_id": comment_id_index, 
                                        "parent_comment_id": "", 
                                        "comment": comment_text, 
                                        "likes": comment['numRecommends'], 
                                        "dislikes": 0
                                    }
                
                # Add new comment to the dataframe
                comments_df = pd.concat([comments_df, pd.DataFrame([extracted_comment])], ignore_index=True)

                # Update comment_id_index as a comment has been added to the dataframe
                parent_comment_id_index = comment_id_index
                comment_id_index += 1

                # Process the replies
                if 'responses' in comment:
                    for reply in comment['responses']:
                        # Clean reply text
                        reply_text = reply['body']
                        soup = BeautifulSoup(reply_text, "html.parser")
                        reply_text = soup.get_text()

                        extracted_reply =   {
                                                "comment_id": comment_id_index, 
                                                "parent_comment_id": parent_comment_id_index, 
                                                "comment": reply_text, 
                                                "likes": reply['numRecommends'], 
                                                "dislikes": 0
                                            }
                        
                        # Add new reply to the dataframe
                        comments_df = pd.concat([comments_df, pd.DataFrame([extracted_reply])], ignore_index=True)
                        
                        # Update comment_id_index as a reply has been added to the dataframe
                        comment_id_index += 1

        logging.info("Extracted %d comments from %s" % (len(comments_df), original_article_url))

        return comments_df
    
    
    def __get_total_amount_of_pages(self, original_article_url):
        """
        Get the total amount of pages that have comments
        """
        comment_data = self.__fetch_comment_data(original_article_url)
        return comment_data['pages']


    def __fetch_comment_data(self, original_article_url, page=1):
        """
        Retrieves the raw comment data from Daily Mail
        """
        article_url = self.__generate_comment_embed_url(original_article_url)

        # Receive HTTP 403 unless given this header. This tricks the server into thinking an actual web browser is accessing the data
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        params = {
            "page": page,
            "maxResponses": 100
        }

        response = requests.get(article_url, params=params, headers=headers)


        data = ""
        if response.status_code == 200:
            logging.info("Received HTTP GET request (%s)" % article_url)
            data = response.json()
        else:
            logging.info("Error extracting comments for %s" % article_url)

        return data     
    

    def __generate_comment_embed_url(self, original_article_url):
        """
        The Guardian comments are stored at a different URL. This function converts the given URL to the
        URL where the comments are stored at.
        """
        print(original_article_url)
        return {
                    'https://www.theguardian.com/commentisfree/2021/oct/22/england-covid-ethics-personal-responsibility': 'https://discussion.theguardian.com/discussion-api/discussion/p/jazhy',
                    'https://www.theguardian.com/commentisfree/2021/dec/09/johnson-britain-equal-cambridge-rich-poor': 'https://discussion.theguardian.com/discussion-api/discussion/p/jqen8',
                }[original_article_url]
    