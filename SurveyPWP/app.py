from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection

# Configuring and setting up the database for usage. 
app = Flask("SurveyPWP")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Enforcing foreign key constraints which needs a manual configuration.
# Code taken from Kiran Jonnalagadda, https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

"""
Table : Questionnaire
----------------------
Description : This table stores all the questionnaires.

- 'id', INTEGER, PRIMARY KEY, Contains id of each questionnaire.
- 'title', STRING, MAX 64 Characters, NOT NULL, Contains the title of each questionnaire.
- 'description', STRING, MAX 512 Characters, NULLABLE, Contains the description of each questionnaire.

* 'question', RELATIONSHIP with the Question table.
"""
class Questionnaire(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(64), nullable = False)
	description = db.Column(db.String(512), nullable = True)

	question = db.relationship("Question", back_populates = "questionnaire", cascade = "save-update, delete")
	session = db.relationship("Session",back_populates = "questionnaire")
"""
Table : Question
----------------------
Description : This table stores all the questions, and each question belongs to a specific questionnaire.

- 'id', INTEGER, PRIMARY KEY, Contains id of each question.
- 'questionnaire_id', INTEGER, FOREIGN KEY, NOT NULL, Contains id of the questionnaire.
- 'title', STRING, MAX 64 Characters, NOT NULL, Contains the title of each question.
- 'description', STRING, MAX 512 Characters, NULLABLE, Contains the description of each question.

* 'questionnaire', RELATIONSHIP with the Questionnaire table.
* 'answer', RELATIONSHIP with the Answer table.
"""
class Question(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable = False)
	title = db.Column(db.String(64), nullable = False)
	description = db.Column(db.String(512), nullable = True)

	questionnaire = db.relationship("Questionnaire", back_populates = "question")
	answer = db.relationship("Answer", back_populates = "question", cascade = "save-update, delete")

"""
Table : Answer
----------------------
Description : This table stores all the answers, and each answer belongs to a specific question.

- 'id', INTEGER, PRIMARY KEY, Contains id of each answer.
- 'question_id', INTEGER, FOREIGN KEY, NULLABLE, Contains id of the question.
- 'content', STRING, MAX 512 Characters, NOT NULL, Contains the answer as a string.

* 'question', RELATIONSHIP with the Question table.
"""
class Answer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable = False)
	content = db.Column(db.String(512), nullable = False)

	question = db.relationship("Question", back_populates = "answer")
	session = db.relationship("Session",back_populates = "answer")
"""
Table : Session
----------------------
Description : 

"""
class Session(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable = False)
	answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"), nullable = False)
	
	questionnaire = db.relationship("Questionnaire", back_populates = "session")
	answer = db.relationship("Answer", back_populates = "session")