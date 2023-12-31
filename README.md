# covid-blame

## Extracting comments

### 1. Articles Spreadsheet

The spreadsheet containing the list of articles and their URLs must be stored under `data/raw/`. The scripts attempt to load this spreadsheet.

### 2. Extracting comment scripts

`extract_comments.py` will attempt to extract comments from articles. The Article ID and outlet must be specified when running this script, for example:

`python extract_comments.py dm 242` will extract all comments from Article ID 242 under `Mail Online Only` sheet in the articles spreadsheet.

The script stores each comment and reply in a pandas dataframe, and saves them to: `data/external/comments/source/X.csv`, where `source` is the outlet and `X` is the Article ID.

To extract facebook comments, specify `facebook=true` at the end of the command, such as: `python extract_comments.py guardian 22 facebook=true`.

| Source | Python Argument | author_city | author_country | likes | dislikes |
| --- | --- | --- | --- | --- | --- |
| BBC | bbc | N | N | Y | Y | 
| Daily Mail | dm | Y | Y | Y | Y | 
| Guardian | guardian | N | N | Y | N |
| Facebook | true | N | N | N | N |

## Setting up the Database

### 1. Creating the tables

`python scripts/database/create_db.py` will create an SQLite database with two tables: articles and comments. This needs to be executed first in order to create the tables to later insert data into the database. The articles are loaded from the spreadsheet under `data/raw/`.

### 2. Inserting Articles to the Database

`python scripts/database/populate_db_articles.py` will load the articles spreadsheet in `data/raw/` and insert each article under each sheet into the articles table.

### 3. Inserting Comments to the Database

`python scripts/database/populate_db_comments.py` will iterate through the extracted comment .csvs located in `data/external/comments` for each outlet and article. It will insert the comments into the table and keep the parent_comment_ids. The original comment_id will most likely be replaced as each .csv starts with the comment_id of 1.
