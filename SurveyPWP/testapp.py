from app import db, Questionnaire, Question, Answer
from sqlalchemy import exc, orm, event
from sqlalchemy.engine import Engine

# Enforcing foreign key constraints which needs a manual configuration.
# Code taken from Kiran Jonnalagadda, https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

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


   
