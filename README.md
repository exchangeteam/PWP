# PWP SPRING 2019
# SurveyPWP
# Group information
* Student 1. Berke Esmer and berkee.eesmer@gmail.com
* Student 2. Zifan Xiao and xiao0126@139.com
* Student 3. Mengnanlan Peng and llanan9817@163.com
# Database setup
## Required imformation
The creating of database requires `Flask`, `flask_sqlalchemy`, `sqlite3`. All of these can be installed by using `pip install` command with the name, for example `pip install Flask`. 

We also recommend you to use the following command to install all the librarys you need.
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
After creating an empty database,you can insert some data into the models and test it later. So you can import the `populate_db.py` and there are some functions for populating the database. One example of populating the database is following:
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
By using this function, you can input the data you want to insert and need to run `db.session.commit()`. 

Also, if you want to populate the database quickly, you can use `python populate_db.py`.

There are more documentations and explanation in `populate.py` you can check.

## Database testing 
After populating the database, you can test it now. The testing of database requires `tempfile`, `pytest`, `os`. Then you can use `test_db.py` to test the database automatically. You should put the file `test_db.py` into the same directory of the `app.py`, `populate_db.py` and `database.db`. Then you can run the command `pytest test_db.py`, the database will be tested automatically. The detailed result will be shown after test, so you can see the test passed or failed.

One example of testing functions in `test_db.py` is following:
```python
def test_questionnaire_filter1(db_handle):
	questionnaire = _get_questionnaire()
	db.session.add(questionnaire)
	db.session.commit()

	query_questionnaire = Questionnaire.query.filter_by(title = "Birthday party for Ivan")

	assert query_questionnaire.count() == 1
```

# API setup and testing
If the FLASK has already been set up and the database has been configured properly, you can start to run the API by using the command `flask run`.

The test for API functionalities are in `test_resource.py`. To run the test, you can just use command `pytest test_resource.py`.

# API and client information of our application
Our API can be found in this address: [http://45.76.39.46:5000/api/](http://45.76.39.46:5000/api/)
Our web client can be found in this address: [http://surveypwp.tk/](http://surveypwp.tk/)







