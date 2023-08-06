import logging

import pandas as pd

import facebook_scraper as fs


class FacebookCommentExtractor:
    def extract_comments_from_post(self, post_url):
        logging.info("Extracting comments for %s" % post_url)

        post_id = self.__get_facebook_post_id_from_post_url(post_url)

        comments = self.__fetch_comment_data_from_post_id(post_id)

        # Create a pandas dataframe to store the comments
        comments_df = pd.DataFrame(columns=['comment_id', 'parent_comment_id', 'comment', 'likes', 'dislikes'])
        comment_id_index = 1
        parent_comment_id_index = 1


        # Process comments
        for comment in comments:
            extracted_comment = {
                                    "comment_id": comment_id_index, 
                                    "parent_comment_id": 0,
                                    "comment": comment['comment_text'], 
                                    "likes": 0, 
                                    "dislikes": 0
                                }
            
            # Add new comment to the dataframe
            comments_df = pd.concat([comments_df, pd.DataFrame([extracted_comment])], ignore_index=True)

            # Update comment_id as new comment added
            comment_id_index += 1

            for reply in comment['replies']:
                extract_reply = {
                                    "comment_id": comment_id_index, 
                                    "parent_comment_id": parent_comment_id_index, 
                                    "comment": reply['comment_text'], 
                                    "likes": 0, 
                                    "dislikes": 0    
                                }
                
                # Add new comment to the dataframe
                comments_df = pd.concat([comments_df, pd.DataFrame([extract_reply])], ignore_index=True)

                # Update comment_id as new comment added
                comment_id_index += 1

            # Update parent_comment_id as replies processed
            parent_comment_id_index = comment_id_index


        logging.info("Extracted %d comments from %s" % (len(comments_df), post_url))

        return comments_df
    

    def __fetch_comment_data_from_post_id(self, facebook_post_id):
        gen = fs.get_posts(
            post_urls=[facebook_post_id],
            options={
                "comments": True, 
                "progress": True
            },
            cookies={
                "xs": "",
                "c_user": ""
            }
        )

        post = next(gen)
        comments = post['comments_full']

        return comments
    
    def __get_facebook_post_id_from_post_url(self, facebook_post_url):
        """
        Get the Post ID from the Facebook Post URL
        """
        return facebook_post_url.split("/")[5].replace("?locale=en_GB", "")
