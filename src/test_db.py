import app as app
import populate_db as populate
import pytest, os, tempfile
from app import db, Questionnaire, Question, Answer
from sqlalchemy import event, update, exc
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

#Below function is taken from the Exercise 1: Testing Flask Applications, on Lovelace
@pytest.fixture
def db_handle():
	"""
	This function is making a preparation before testing.
	Before every test that has 'db_handle' as its parmeter, this function will run.
	Thus, every test will have a individual temporary database.
	Code adapted from 'After Exercise 1': Testing Flask Application
	"""
	db_fd, db_fname = tempfile.mkstemp()
	app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
	app.app.config["TESTING"] = True

	with app.app.app_context():
		app.db.create_all()

	yield app.db

	os.close(db_fd)
	os.unlink(db_fname)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def _get_questionnaire():
	"""
	An example of questionnaire.
	"""
	questionnaire = Questionnaire(
		title = "Birthday party for Ivan", 
		description = "We are organizing a birthday party for Ivan. He is going to be so happy!"
		)

	return questionnaire

def _get_question(_questionnaire):
	"""
	An example of question in a specific questionnaire.
	"""
	question = Question(
		title = "Choose a date",
		description = "Between 1st of March and 4th of March, please tell us the dates you are available.",
		questionnaire = _questionnaire
		)

	return question

def _get_answer(_question,_userName):
	"""
	An example of answer to a specific question
	"""
	answer = Answer(
		content = "Everyday is okay!",
		question = _question,
		userName = _userName
		)
	return answer

def _get_userName(option=0):
	"""
	Example of userNames.
	"""
	userName = ["A","B","C","user4","user5"]
	return userName[option]

#error scenarios
def test_create_questionnaire(db_handle):
	"""
	Tests that we can create an instance of questionnaire and check if it's in the database.
	"""
	questionnaire = _get_questionnaire()
	db.session.add(questionnaire)
	db.session.commit()

	assert Questionnaire.query.count() == 1, "Creating questionnaire is failed."

def test_create_question(db_handle):
	"""
	Tests that we can create an instance of question and check if it's in the database.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.commit()

	assert Question.query.count() == 1, "Creating question is failed."

def test_create_answer(db_handle):
	"""
	Tests that we can create an instance of answer and check if it's in the database.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(0))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	assert Answer.query.count() == 1, "Creating question is failed."

def test_null_questionnaire_title(db_handle):
	"""
	Tests whether a questionnaire can be created without a title or not.
	"""
	questionnaire = Questionnaire(description="this is a non-title test")
	db.session.add(questionnaire)
	with pytest.raises(exc.IntegrityError):
		db.session.commit() 

def test_null_question_title(db_handle):
	"""
	Tests whether a question can be created without a title or not.
	"""
	questionnaire = _get_questionnaire()
	question1 = Question(questionnaire=questionnaire,description="this is a non-title test")
	question2 = Question(title="test",description="this is a non-questionnaire test")
	db.session.add(questionnaire)
	db.session.add(question1)
	db.session.add(question2)
	with pytest.raises(exc.IntegrityError):
		db.session.commit() 

def test_null_answer(db_handle):
	"""
	Tests whether an answer can be created without its content or userName. 
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer1 = Answer(question=question,userName="Non-content-tester")
	answer2 = Answer(content = "This is a non-question test",userName = "Non-userName-tester")
	answer3 = Answer(question = question,content ="This is a non-userName test")
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer1)
	db.session.add(answer2)
	db.session.add(answer3)
	with pytest.raises(exc.IntegrityError):
		db.session.commit() 

def test_delete_questionnaire(db_handle):
	"""
	Tests that we can delete an empty questionnaire.
	"""
	questionnaire = _get_questionnaire()
	db.session.add(questionnaire)
	db.session.commit()

	query_questionnaire = Questionnaire.query.first()
	db.session.delete(query_questionnaire)
	db.session.commit()

	assert Questionnaire.query.count() == 0, "Deleting questionnaire is failed"

def test_delete_question(db_handle):
	"""
	Tests that we can delete a question that has answers.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.commit()

	query_question = Question.query.first()
	db.session.delete(query_question)
	db.session.commit()

	assert Question.query.count() == 0, "Deleting question is failed"

def test_delete_answer(db_handle):
	"""
	Tests that we can delete an answer and check if it is in the database.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(0))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	query_answer = Answer.query.first()
	db.session.delete(query_answer)
	db.session.commit()

	assert Answer.query.count() == 0, "Deleting answer is failed"

def test_question_ondelete_answer(db_handle):
	""" 
	Tests that we can delete a question that has answers 
	and check if they are in the database.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(0))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	query_question = Question.query.first()
	db.session.delete(query_question)
	db.session.commit()

	assert  Answer.query.count() == 0 and Question.query.count() == 0, "Failed to delete the question and its answers."

def test_question_ondelete_answer(db_handle):
	""" 
	Tests that we can delete a whole questionnaire that has questions and answers 
	and check if they are in the database.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(0))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	query_questionnaire = Questionnaire.query.first()
	db.session.delete(query_questionnaire)
	db.session.commit()

	assert  Questionnaire.query.count() == 0 and Answer.query.count() == 0 and Question.query.count() == 0, "Failed to delete the questionnaire and questions with their answers."

def test_update_questionnaire(db_handle):
	"""
	Tests that we can update the title of a questionnaire.
	"""
	questionnaire = _get_questionnaire()
	db.session.add(questionnaire)
	db.session.commit()

	query_questionnaire = Questionnaire.query.first()
	query_questionnaire.title = "Birthday party is not for Ivan, it is for Berke."
	db.session.commit()

	assert query_questionnaire.title == "Birthday party is not for Ivan, it is for Berke."

def test_update_question(db_handle):
	"""
	Tests that we can update a question title in questionnaire.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.commit()

	query_question = Question.query.first()
	query_question.title = "Just say a date."
	db.session.commit()

	assert query_question.title == "Just say a date."

def test_update_answer(db_handle):
	"""
	Tests that we can update an answer to one question.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(0))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	query_answer = Answer.query.first()
	query_answer.content = "I am too busy to come your parties. Do not invite me again!"
	db.session.commit()

	assert query_answer.content == "I am too busy to come your parties. Do not invite me again!"

def test_questionnaire_filter1(db_handle):
	"""
	Tests retriving an existing instance of questionnaire by its title.
	"""
	questionnaire = _get_questionnaire()
	db.session.add(questionnaire)
	db.session.commit()

	query_questionnaire = Questionnaire.query.filter_by(title = "Birthday party for Ivan")

	assert query_questionnaire.count() == 1

def test_questionnaire_filter2(db_handle):
	"""
	Tests retriving an existing instance of questionnaire by its title.
	"""
	questionnaire = _get_questionnaire()
	db.session.add(questionnaire)
	db.session.commit()

	query_questionnaire = Questionnaire.query.filter_by(title = "Birthday party for Berke")

	assert query_questionnaire.count() == 0

def test_question_filter1(db_handle):
	"""
	Tests retriving an existing instance of question by its title.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.commit()

	query_question = Question.query.filter_by(title = "Choose a date")

	assert query_question.count() == 1

def test_question_filter2(db_handle):
	"""
	Tests retriving a non-existent instance of question by its title.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.commit()

	query_question = Question.query.filter_by(title = "Choose a gift")

	assert query_question.count() == 0

def test_answer_filter1(db_handle):
	"""
	Tests retriving an existing instance of answer by its content.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(0))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	query_answer = Answer.query.filter_by(content = "Everyday is okay!")

	assert query_answer.count() == 1

def test_answer_filter2(db_handle):
	"""
	Tests retriving an non-existent instance of question by its content.
	"""
	questionnaire = _get_questionnaire()
	question = _get_question(questionnaire)
	answer = _get_answer(question,_get_userName(1))
	db.session.add(questionnaire)
	db.session.add(question)
	db.session.add(answer)
	db.session.commit()

	query_answer = Answer.query.filter_by(content = "I am all busy")

	assert query_answer.count() == 0

# END OF TEST