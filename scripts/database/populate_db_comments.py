import logging
from pathlib import Path

import pandas as pd
import sqlite3


logging.basicConfig(format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

DATABASE_PATH = Path("data/processed/covid-blame.db")

# Load database
logging.info("Connecting to database")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

folder_sources = {
    'bbc': 'BBC',
    'dailymail': 'Daily Mail',
    'guardian': 'The Guardian',
    'facebook': 'Facebook'
}

# Loop through each folder
for folder, source in folder_sources.items():
    folder_path = Path('data/external/comments') / folder
    
    # Check if the folder exists
    if folder_path.exists() and folder_path.is_dir():

        # Loop through each file
        for file in folder_path.iterdir():
            if file.is_file():
                logging.info(f"Processing comments in {file}")

                # Load the comments from the file
                comment_df = pd.read_csv(file)
                article_id = file.name.split(".")[0]

                # Process each comment
                for comment_row_tuple in comment_df.itertuples():

                    logging.info(f"Processing comment_id {comment_row_tuple.comment_id}")
                    

                    # Insert comment into db
                    if hasattr(comment_row_tuple, "author_city"):
                        insert_comment_query =  """
                                        INSERT INTO comments (comment, article_id, author_city, author_country, likes, dislikes, source)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                        """


                        cursor.execute(insert_comment_query, 
                                        (
                                            comment_row_tuple.comment, 
                                            article_id, 
                                            comment_row_tuple.author_city, 
                                            comment_row_tuple.author_country, 
                                            comment_row_tuple.likes, 
                                            comment_row_tuple.dislikes, 
                                            source
                                        )
                                    )
                    else:
                        insert_comment_query =  """
                                        INSERT INTO comments (comment, article_id, likes, dislikes, source)
                                        VALUES (?, ?, ?, ?, ?)
                                        """


                        cursor.execute(insert_comment_query, 
                                        (
                                            comment_row_tuple.comment, 
                                            article_id, 
                                            comment_row_tuple.likes, 
                                            comment_row_tuple.dislikes, 
                                            source
                                        )
                                    )
                        
                    conn.commit()

                    # Check if the parent_comment_id needs to be inserted into the database
                    # if pd.notna(comment_row_tuple.parent_comment_id) or comment_row_tuple.parent_comment_id != "0":
                    if pd.notna(comment_row_tuple.parent_comment_id) and comment_row_tuple.parent_comment_id != 0:
                        # Get the new comment_id for the child comment for the update query
                        comment_id_from_db = cursor.lastrowid

                        # Get the parent comment from the dataframe
                        parent_comment_row = comment_df[comment_df['comment_id'] == comment_row_tuple.parent_comment_id]
                        parent_comment = parent_comment_row.iloc[0]['comment']

                        # Retrieve the new comment_id from the database for the parent comment
                        cursor.execute("SELECT comment_id FROM comments WHERE comment = ?", (parent_comment,))
                        result = cursor.fetchone()
                        parent_comment_id_from_db = result[0]

                        # Update the child's comment parent_comment_id in the database with the new parent's comment_id
                        cursor.execute("UPDATE comments SET parent_comment_id = ? WHERE comment_id = ?", (parent_comment_id_from_db, comment_id_from_db))
                        conn.commit()


# Save the changes to the file
conn.commit()
conn.close()
logging.info("Saved database")
