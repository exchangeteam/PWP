from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

# Configuring and setting up the database for usage. 
app = Flask("SurveyPWP")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Enforcing foreign key constraints which needs a manual configuration.
# Code taken from Kiran Jonnalagadda, https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
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

	question = db.relationship("Question", back_populates = "questionnaire")

"""
Table : Question
----------------------
Description : This table stores all the questions, and each question belongs to a specific questionnaire.

- 'id', INTEGER, PRIMARY KEY, Contains id of each question.
- 'questionnaire_id', INTEGER, FOREIGN KEY & PRIMARY KEY, Contains id of each questionnaire.
- 'title', STRING, MAX 64 Characters, NOT NULL, Contains the title of each question.
- 'description', STRING, MAX 512 Characters, NULLABLE, Contains the description of each question.

* 'questionnaire', RELATIONSHIP with the Questionnaire table.
* 'answer', RELATIONSHIP with the Answer table.
"""
class Question(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), primary_key = True)
	title = db.Column(db.String(64), nullable = False)
	description = db.Column(db.String(512), nullable = True)

	questionnaire = db.relationship("Questionnaire", back_populates = "question")
	answer = db.relationship("Answer", back_populates = "question")

"""
Table : Answer
----------------------
Description : This table stores all the answers, and each answer belongs to a specific question.

- 'id', INTEGER, PRIMARY KEY, Contains id of each answer.
- 'question_id', INTEGER, FOREIGN KEY & PRIMARY KEY, Contains id of each question.
- 'content', STRING, MAX 512 Characters, NOT NULL, Contains the answer as a string.

* 'question', RELATIONSHIP with the Question table.
"""
class Answer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key = True)
	content = db.Column(db.String(512), nullable = False)

	question = db.relationship("Question", back_populates = "answer")
	
