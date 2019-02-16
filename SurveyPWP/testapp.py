from app import db, Questionnaire, Question, Answer
from sqlalchemy import exc, orm, event, update
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
import populate_db as populate
import pytest

# Enforcing foreign key constraints which needs a manual configuration.
# Code taken from Kiran Jonnalagadda, https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

def test_create_questionnaire():
	populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	db.session.commit()

	assert Questionnaire.query.count() == 1, "Creating questionnaire is failed."
	db.session.rollback()

def test_create_question():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	populate.create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
	db.session.commit()

	assert Question.query.count() == 1, "Creating question is failed."
	db.session.rollback()

def test_create_answer():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	first_question = populate.create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
	populate.create_answer("Everyday is okay!", first_question)
	db.session.commit()

	assert Answer.query.count() == 1, "Creating question is failed."
	db.session.rollback()

def test_delete_questionnaire():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	db.session.commit()

	query_questionnaire = Questionnaire.query.first()
	db.session.delete(query_questionnaire)
	db.session.commit()

	assert Questionnaire.query.count() == 0, "Deleting questionnaire is failed"
	db.session.rollback()

def test_delete_question():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	first_question = populate.create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
	db.session.commit()

	query_question = Question.query.first()
	db.session.delete(query_question)
	db.session.commit()

	assert Question.query.count() == 0, "Deleting question is failed"
	db.session.rollback()

def test_delete_answer():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	first_question = populate.create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
	first_answer = populate.create_answer("Everyday is okay!", first_question)	
	db.session.commit()

	query_answer = Answer.query.first()
	db.session.delete(query_answer)
	db.session.commit()

	assert Answer.query.count() == 0, "Deleting answer is failed"
	db.session.rollback()

def test_update_questionnaire():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	db.session.commit()

	query_questionnaire = Questionnaire.query.first()
	query_questionnaire.title = "Birthday party is not for Ivan, it is for Berke."
	db.session.commit()

	assert query_questionnaire.title == "Birthday party is not for Ivan, it is for Berke."
	db.session.rollback()

def test_update_question():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	first_question = populate.create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
	db.session.commit()

	query_question = Question.query.first()
	query_question.title = "Just say a date."
	db.session.commit()

	assert query_question.title == "Just say a date."
	db.session.rollback()

def test_update_answer():
	first_questionnaire = populate.create_questionnaire("Birthday party for Ivan", "We are organizing a birthday party for Ivan. He is going to be so happy!")
	first_question = populate.create_question("Choose a date", first_questionnaire, "Between 1st of March and 4th of March, please tell us the dates you are available.")
	first_answer = populate.create_answer("Everyday is okay!", first_question)	
	db.session.commit()

	query_answer = Answer.query.first()
	query_answer.content = "I am too busy to come your parties. Do not invite me again!"
	db.session.commit()

	assert query_answer.content == "I am too busy to come your parties. Do not invite me again!"
	db.session.rollback()