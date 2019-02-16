# PWP SPRING 2019
# SurveyPWP
# Group information
* Student 1. Berke Esmer and berkee.eesmer@gmail.com
* Student 2. Zifan Xiao and xiao0126@139.com
* Student 3. Mengnanlan Peng and llanan9817@163.com
# Database setup
## Required imformation
The creating of database requires `Flask`, `flask_sqlalchemy`, `sqlite3`. All of these can be installed by using `pip install` command with the name, like `pip install Flask`.
## Creating the database
Tha data base can be created by running two lines of code: 
```python
from database import db
db.create_all()
```
Then an empty database named `test.db` is in the same directory where your code is.
## Populating the database

## Database testing 
After creating the database, we should test it now. The testing of database requires `sqlalchemy`, `sqlite3`, `populate_db`, `pytest`.








