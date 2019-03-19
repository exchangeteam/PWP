from app import db, Questionnaire, Question, Answer
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

# Enforcing foreign key constraints which need a manual configuration.
# Code taken from Kiran Jonnalagadda, https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def create_db():
	"""
	Create the database tables and set everyting ready.
	"""
	db.create_all()
	print("Database is created!")
	print("--------------------")

def create_questionnaire(_title, _description=""):
	"""
	Create a questionnaire with title and description.
	Titles are mandatory while descriptions are optional.
	"""
	if(_description != ""):
		questionnaire = Questionnaire(title = _title, description = _description)
	else:
		questionnaire = Questionnaire(title = _title)

	db.session.add(questionnaire)
	print("A new questionnaire is created.")
	print("Title: ", _title)
	print("Description: ", _description)
	print("--------------------")
	return questionnaire

def create_question(_title, _questionnaire, _description=""):
	"""
	Create a question with title and description.
	Titles are mandatory while descriptions are optional.
	It's also mandatory to put it into a specific questionnaire.
	"""
	if(_description != ""):
		question = Question(title = _title, description = _description, questionnaire = _questionnaire)
	else:
		question = Question(title = _title, questionnaire = _questionnaire)

	db.session.add(question)
	print("A new question is created.")
	print("Title: ", _title)
	print("Description: ", _description)
	print("--------------------")
	return question



def create_answer(_content, _question, _userName):
	"""
	Create an answer to one question.
	Content of the answer and the username of the user are required.
	It's also mandatory to put it into a specific questionnaire.
	"""
	answer = Answer(content = _content, question = _question, userName = _userName)
	db.session.add(answer)
	print("A new answer is created by", _userName)
	print("Content: ", _content)
	print("--------------------")
	return answer

#Main function
create_db()

first_questionnaire = create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
first_question = create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
second_question = create_question("How many people are you coming with?", first_questionnaire)
third_question = create_question("Is there any theme in your mind for the birthday party?", first_questionnaire)
first_answer = create_answer("Everyday is okay!", first_question, "user1")
second_answer = create_answer("Three people: Berke, Alina, Xiao", second_question, "user1")
thirds_answer = create_answer("Star Wars theme.", third_question, "user1")

db.session.commit()
