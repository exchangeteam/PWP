from app import db, Questionnaire, Question, Answer
from sqlalchemy import exc, orm, event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

# Enforcing foreign key constraints which need a manual configuration.
# Code taken from Kiran Jonnalagadda, https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

def create_db():
	print("Database is created!")
	print("--------------------")

	db.create_all()

def create_questionnaire(_title, _description=""):
	if(_description != ""):
		questionnaire = Questionnaire(title = _title, description = _description)
	else:
		questionnaire = Questionnaire(title = _title)

	print("A new questionnaire is created.")
	print("Title: ", _title)
	print("Description: ", _description)
	print("--------------------")

	db.session.add(questionnaire)
	return questionnaire

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

def create_answer(_content, _question):
	answer = Answer(content = _content, question = _question)

	print("A new answer is created.")
	print("Content: ", _content)
	print("--------------------")

	db.session.add(answer)
	return answer

# Main function
create_db()

first_questionnaire = create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
first_question = create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
second_question = create_question("How many people are you coming with?", first_questionnaire)
third_question = create_question("Is there any theme in your mind for the birthday party?", first_questionnaire)
first_answer = create_answer("Everyday is okay!", first_question)
second_answer = create_answer("Three people: Berke, Alina, Xiao", second_question)
thirds_answer = create_answer("Star Wars theme.", third_question)

db.session.commit()