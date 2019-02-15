from flask import Flask
from flask_sqlalchemy import SQLAlchemy




app = Flask("SurveyPWP")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Questionnaire(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(64), nullable = False)
	description = db.Column(db.String(512), nullable = True)

	question = db.relationship("Question", back_populates = "questionnaire")

class Question(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), primary_key = True)
	title = db.Column(db.String(64), nullable = False)
	description = db.Column(db.String(512), nullable = True)

	questionnaire = db.relationship("Questionnaire", back_populates = "question")
	answer = db.relationship("Answer", back_populates = "question")

class Answer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key = True)
	content = db.Column(db.String(512), nullable = False)

	question = db.relationship("Question", back_populates = "answer")
