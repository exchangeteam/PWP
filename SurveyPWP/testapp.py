from app import db, Questionnaire, Question, Answer
from sqlalchemy import exc
from sqlalchemy import orm

db.create_all()

try:
	questionnaire = Questionnaire(title = "Xiao")
	db.session.add(questionnaire)
	db.session.commit()

	answer = Answer(content = "asda")
	db.session.add(answer)
	db.session.commit()

except exc.IntegrityError:
	print("A not nullable element is not submitted.")
except orm.exc.FlushError:
	print("A primary key is not submitted.")
except KeyError:
	print("Wrong target is submitted as key.")


