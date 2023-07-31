# covid-blame

## Extracting comments

### 1. Articles Spreadsheet

The spreadsheet containing the list of articles and their URLs must be stored under `data/raw/`. The scripts attempt to load this spreadsheet.

### 2. Extracting comment scripts

#### Daily Mail

`extract_comments_dailymail.py` will attempt to extract comments from Daily Mail articles. The Article ID must be specified when running this script, for example:

`python extract_comments_dailymail.py 242` will extract all comments from Article ID 242 under `Mail Online Only` sheet in the articles spreadsheet.

The script stores each comment and reply in a pandas dataframe, and saves them to: `data/external/comments/dailymail/X.csv`, where X is the Article ID.

## Setting up the Database

### 1. Creating the tables

`python scripts/database/create_db.py` will create an SQLite database with two tables: articles and comments. This needs to be executed first in order to create the tables to later insert data into the database.
