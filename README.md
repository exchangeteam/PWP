# PWP SPRING 2019
# SurveyPWP
# Group information
* Student 1. Berke Esmer and berkee.eesmer@gmail.com
* Student 2. Zifan Xiao and xiao0126@139.com
* Student 3. Mengnanlan Peng and llanan9817@163.com
# Database setup
## Required imformation
The creating of database requires `Flask`, `flask_sqlalchemy`, `sqlite3`. All of these can be installed by using `pip install` command with the name, for example `pip install Flask`. We also recommend you to use the following command to install all the librarys you need.
```python
pip install -r requirements.txt
``` 
## Creating the database
Tha data base can be created by running two lines of code: 
```python
from database import db
db.create_all()
```
Then an empty database named `database.db` is in the same directory where your code is.
## Populating the database
After creating an empty database,you can insert some data into the models and test it later. So you can import the `populate_db.py` and there are some functions for populating the database. One example of creating a table is following:
```python
def create_question(_title, _questionnaire, _description=""):
	if(_description != ""):
		question = Question(title = _title, description = _description, questionnaire = _questionnaire)
	else:
		question = Question(title = _title, questionnaire = _questionnaire)

	print("A new question is created.")
	print("Title: ", _title)
	print("Description: ", _description)
	print("--------------------")

	db.session.add(question)
	return question
```

## Database testing 
After creating the database, we should test it now. The testing of database requires `sqlalchemy`, `sqlite3`, `populate_db`, `pytest`.








