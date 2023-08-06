# covid-blame

## Extracting comments

### 1. Articles Spreadsheet

The spreadsheet containing the list of articles and their URLs must be stored under `data/raw/`. The scripts attempt to load this spreadsheet.

### 2. Extracting comment scripts

`extract_comments.py` will attempt to extract comments from articles. The Article ID and outlet must be specified when running this script, for example:

`python extract_comments.py dm 242` will extract all comments from Article ID 242 under `Mail Online Only` sheet in the articles spreadsheet.

The script stores each comment and reply in a pandas dataframe, and saves them to: `data/external/comments/dailymail/X.csv`, where X is the Article ID.

| Source | Python Argument | author_city | author_country | likes | dislikes |
| --- | --- | --- | --- | --- | --- |
| BBC | bbc | N | N | Y | Y | 
| Daily Mail | dm | Y | Y | Y | Y | 
| Guardian | guardian | N | N | Y | N |

## Setting up the Database

### 1. Creating the tables

`python scripts/database/create_db.py` will create an SQLite database with two tables: articles and comments. This needs to be executed first in order to create the tables to later insert data into the database. The articles are loaded from the spreadsheet under `data/raw/`.

### 2. Inserting Articles to the Articles Table

`python scripts/database/populate_db_articles.py` will load the articles spreadsheet in `data/raw/` and insert each article under each sheet into the articles table.
