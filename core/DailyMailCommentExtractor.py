import re
import requests
import logging

import pandas as pd


class DailyMailCommentExtractor():
    def extract_comments_from_original_article_url(self, original_article_url):
        """
        Main function to extract all of the comments
        """
        logging.info("Extracting comments for %s" % original_article_url)

        # Create a pandas dataframe to store the comments
        comments_df = pd.DataFrame(columns=['comment_id', 'parent_comment_id', 'comment', 'author_city', 'author_country', 'likes', 'dislikes'])

        # Track the comment_id and parent_comment_id of each comment
        comment_id_index = 1
        parent_comment_id_index = 1


        # Fetch the comments
        comment_data = self.__fetch_comment_data(original_article_url)

        # Process and extract all comments
        for comment in comment_data['payload']['page']:
            author_city, author_country = self.__get_author_city_and_country_from_comment(comment)

            # Extract the data needed
            extracted_comment = {
                        'comment_id': comment_id_index, 
                        'parent_comment_id': "", 
                        'comment': comment['message'],
                        'author_city': author_city,
                        'author_country': author_country,
                        'likes': str((comment['voteRating'] + comment['voteCount']) / 2)[:-2], 
                        'dislikes': str(abs((comment['voteRating'] - comment['voteCount']) / 2))[:-2]
                    }
            comments_df = pd.concat([comments_df, pd.DataFrame([extracted_comment])], ignore_index=True)

            # Update comment_id_index as a comment has been added to the dataframe
            comment_id_index += 1


            # Process the replies
            for reply in comment['replies']['comments']:
                author_city, author_country = self.__get_author_city_and_country_from_comment(reply)

                extracted_reply = {
                            "comment_id": comment_id_index, 
                            "parent_comment_id": parent_comment_id_index, 
                            "comment": reply['message'],
                            "author_city": author_city,
                            "author_country": author_country,
                            "likes": str((reply['voteRating'] + reply['voteCount']) / 2)[:-2], 
                            "dislikes": str(abs((reply['voteRating'] - reply['voteCount']) / 2))[:-2]
                        }
                comments_df = pd.concat([comments_df, pd.DataFrame([extracted_reply])], ignore_index=True)
                
                # Update comment_id_index as a reply has been added to the dataframe
                comment_id_index += 1

            # Update the parent_comment_id_index as the replies have now been processed
            parent_comment_id_index = comment_id_index


        logging.info("Extracted %d comments from %s" % (len(comments_df), original_article_url))

        return comments_df


    def __fetch_comment_data(self, original_article_url):
        """
        Retrieves the raw comment data from Daily Mail
        """
        article_url = self.__generate_comment_embed_url(original_article_url)

        # Receive HTTP 403 unless given this header. This tricks the server into thinking an actual web browser is accessing the data
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(article_url, headers=headers)


        data = ""
        if response.status_code == 200:
            logging.info("Received HTTP GET request (%s)" % article_url)
            data = response.json()
        else:
            logging.info("Error extracting comments for %s" % article_url)

        return data        


    def __generate_comment_embed_url(self, original_article_url):
        """
        Daily Mail articles are accessed at https://www.dailymail.co.uk/news/article-8540619/Chris-Whitty-defends-coronavirus-lockdown-lag-bad-tempered-interview.html,
        however the comments are stored at a different URL, e.g.: https://www.dailymail.co.uk/reader-comments/p/asset/readcomments/8540619?max=1000000&order=desc
        This function converts the normal URL to the URL where just the comments are stored
        """
        match = re.search("(?<=article-)\d+", original_article_url)
        if match:
            article_id = match.group()
    
        return "https://www.dailymail.co.uk/reader-comments/p/asset/readcomments/%s?max=1000000&order=desc" % article_id


    def __get_author_city_and_country_from_comment(self, comment):
        """
        Try to extract the author's city and country, depending on what they have set it to, e.g.: "Liverpool, United Kingdom".
        If there is no comma in the location (e.g. "Bournemouth"), it will be stored in the city. This function may return a country
        if they have set the location to just their country.
        """
        if ',' in comment['userLocation']:
            author_city, author_country = comment['userLocation'].split(',', 1)
            author_city = author_city.strip()
            author_country = author_country.strip()
        else:
            author_city = comment['userLocation']
            author_country = ''

        return author_city, author_country
