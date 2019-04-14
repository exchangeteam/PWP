import json
import collections
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from flask_restful import Api
from jsonschema import validate, ValidationError
from sqlite3 import Connection as SQLite3Connection

# Configuring and setting up the database for usage. 
app = Flask("SurveyPWP")
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

QUESTIONNAIRE_PROFILE = "/profiles/questionnaire/"
QUESTION_PROFILE = "/profiles/question/"
ANSWER_PROFILE = "/profiles/answer/"
LINK_RELATIONS_URL = "/survey/link-relations/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

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
- 'userName', STRING, MAX 64 Characters, NOT NULL, Contains the username of the user.

* 'question', RELATIONSHIP with the Question table.
"""
class Answer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable = False)
	content = db.Column(db.String(512), nullable = False)
	userName = db.Column(db.String(64), nullable = False)

	question = db.relationship("Question", back_populates = "answer")

db.create_all()

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href
    
    def questionnaire_schema(self):
        schema = {
            "type": "object",
            "required": ["title"],
            "nullable": ["description"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Questionnaire's title",
            "type": "string"
        }
        props["description"] = {
            "description": "Questionnaire's description",
            "type": "string"
        }
        return schema

    def question_schema(self):
        schema = {
            "type": "object",
            "required": ["title"],
            "nullable": ["description"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Question's title",
            "type": "string"
        }
        props["description"] = {
            "description": "Question's description",
            "type": "string"
        }
        return schema
        
    def answer_schema(self):
        schema = {
            "type": "object",
            "required": ["content","userName"]
        }
        props = schema["properties"] = {}
        props["content"] = {
            "description": "Answer's content",
            "type": "string"
        }
        props["userName"] = {
            "description": "The user name of this answer's submitter",
            "type": "string"
        }
        return schema
        
    def create_error_response(status_code, title, message=None):
        resource_url = request.path
        body = MasonBuilder(resource_url=resource_url)
        body.add_error(title, message)
        body.add_control("profile", href=ERROR_PROFILE)
        return Response(json.dumps(body), status_code, mimetype=MASON)
        
class InventoryBuilder(MasonBuilder):
	def add_control_all_questionnaires(self):
		self.add_control(
		    "survey:questionnaire-all",
		    "api/questionnaires/",
		    method="GET",
		    title="Get all questionnaires"
		)
	def add_control_delete_questionnaire(self, id):
		self.add_control(
		    "survey:delete",
		    href=api.url_for(QuestionnaireItem, id = id),
		    method="DELETE",
		    title="Delete this questionnaire"
		)
	def add_control_add_questionnaire(self):
		self.add_control(
		    "survey:add-questionnaire",
		    "api/questionnaires/",
		    method="POST",
		    encoding="json",
		    title="Add a new questionnaire",
		    schema=self.questionnaire_schema()
		)
	def add_control_edit_questionnaire(self, id):
		self.add_control(
		    "edit",
		    href=api.url_for(QuestionnaireItem, id = id),
		    method="PUT",
		    encoding="json",
		    title="Edit this questionnaire",
		    schema=self.questionnaire_schema()
		)
		
	def add_control_all_question(self, questionnaire_id):
		self.add_control(
		    "survey:question-of",
		    href="/api/questionnaires/{}/questions/".format(questionnaire_id),
		    method="GET",
		    title="Get all questions of one questionnaire"
		)
	def add_control_add_question(self, questionnaire_id):
		self.add_control(
		    "survey:add-question",
		    href="/api/questionnaires/{}/questions/".format(questionnaire_id),
		    method="POST",
		    encoding="json",
		    title="Add a new question",
		    schema=self.question_schema()
		)
	def add_control_edit_question(self, questionnaire_id, id):
		self.add_control(
		    "edit",
		    "/api/questionnaires/{}/questions/{}/".format(questionnaire_id, id),
		    method="PUT",
		    encoding="json",
		    title="Edit this question",
		    schema=self.question_schema()
		)
	def add_control_delete_question(self, questionnaire_id, id):
		self.add_control(
		    "survey:delete",
		    "/api/questionnaires/{}/questions/{}/".format(questionnaire_id, id),
		    method="DELETE",
		    title="Delete this question"
		)
	
	def add_control_all_answer(self, questionnaire_id, question_id):
		self.add_control(
		    "survey:answer-to",
		    "/api/questionnaires/{}/questions/{}/answers/".format(questionnaire_id, question_id),
		    method="GET",
		    title="Get all answers to one question in one questionnaire"
		)
	def add_control_add_answer(self, questionnaire_id, question_id):
		self.add_control(
		    "survey:add-answer",
		    "/api/questionnaires/{}/questions/{}/answers/".format(questionnaire_id, question_id),
		    method="POST",
		    encoding="json",
		    title="Add a new answer",
		    schema=self.answer_schema()
		)
	def add_control_edit_answer(self, questionnaire_id, question_id, id):
		self.add_control(
		    "edit",
		    "/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, question_id, id),
		    method="PUT",
		    encoding="json",
		    title="Edit this answer",
		    schema=self.answer_schema()
		)
	def add_control_delete_answer(self, questionnaire_id, question_id, id):
		self.add_control(
		    "survey:delete",
		    "/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, question_id, id),
		    method="DELETE",
		    title="Delete this answer"
		)

	

class EntryPoint(Resource):
	def get(self):
		body = InventoryBuilder()
		body.add_namespace("survey", LINK_RELATIONS_URL)
		body.add_control_all_questionnaires()
		return Response(json.dumps(body), 200, mimetype=MASON)

api.add_resource(EntryPoint, "/api/")

class QuestionnaireCollection(Resource):
    def get(self):
        db_questionnaire= Questionnaire.query.all()
        items=[]
        for item in db_questionnaire:
            questionnaire = InventoryBuilder(
                id = item.id,
			    title = item.title,
			    description = item.description
			)
            questionnaire.add_control("self", api.url_for(QuestionnaireItem, id = item.id))
            questionnaire.add_control("profile", QUESTIONNAIRE_PROFILE)
            items.append(questionnaire)
            
        body = InventoryBuilder(
            items = items
        )
        body.add_namespace("survey", LINK_RELATIONS_URL)
        body.add_control("self", "/api/questionnaires/")
        #body.add_control("answer-to-questionnaire", "/api/questionnaire/{}/")
        body.add_control_add_questionnaire()
            
        return Response(json.dumps(body), 200, mimetype=MASON)
		
    def post(self):
        if not request.json:
            return MasonBuilder.create_error_response(415, "Unsupported media type", "Request must be JSON")
				
        try:
            validate(request.json, MasonBuilder.questionnaire_schema(self))
        except ValidationError as e:
            return MasonBuilder.create_error_response(400, "Invalid JSON document", str(e))
		
        questionnaire_id = ''
        try:
            questionnaire = Questionnaire(
                title = request.json["title"],
                description = request.json["description"]
			)
            db.session.add(questionnaire)
            db.session.commit()
            questionanire_id = questionnaire.id
        except KeyError:
            questionnaire = Questionnaire(
			    title = request.json["title"]
			)
            db.session.add(questionnaire)
            db.session.commit()
            questionanire_id = questionnaire.id
            
        return Response(status=201, headers={"Location":"/api/questionnaires/{}/".format(questionanire_id)})

api.add_resource(QuestionnaireCollection, "/api/questionnaires/")

class QuestionnaireItem(Resource):
	def get(self, id):
		db_questionnaire = Questionnaire.query.filter_by(id = id).first()
		if db_questionnaire is None:
			return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(id))
		body = InventoryBuilder(
		    id = db_questionnaire.id,
		    title = db_questionnaire.title,
		    description = db_questionnaire.description
		)
		body.add_namespace("survey", LINK_RELATIONS_URL)
		body.add_control("self", api.url_for(QuestionnaireItem, id = id))
		body.add_control("profile", QUESTIONNAIRE_PROFILE)
		body.add_control("collection", "/api/questionnaires/")
		body.add_control("question-of", api.url_for(QuestionCollection, questionnaire_id = id))
		body.add_control_edit_questionnaire(id)
		body.add_control_delete_questionnaire(id)
		
		return Response(json.dumps(body), 200, mimetype = MASON)
	
	def put(self, id):
		questionnaire = Questionnaire.query.filter_by(id = id).first()
		if questionnaire is None:
			return MasonBuilder.create_error_response(404, "Not found", "No Questionnaire was found with the id {}".format(id))
			
		if not request.json:
			return MasonBuilder.create_error_response(415, "Unsupported media type", "Request must be JSON")
		try:
			validate(request.json, MasonBuilder.questionnaire_schema(self))
		except ValidationError as e:
			return MasonBuilder.create_error_response(400, "Invalid JSON document", str(e))
		    
		try:
		    questionnaire.title = request.json["title"]
		    questionnaire.description = request.json["description"]
		    db.session.commit()
		except KeyError:
			questionnaire.title = request.json["title"]
			db.session.commit()
			
		return Response(status = 204, headers={"Location":api.url_for(QuestionnaireItem, id = id)})
		
	def delete(self, id):
		questionnaire = Questionnaire.query.filter_by(id = id).first()
		if questionnaire is None:
			return MasonBuilder.create_error_response(404, "Not found", "No Questionnaire was found with the id {}".format(id))
		
		db.session.delete(questionnaire)
		db.session.commit()
			
		return Response(status = 204, headers={"Location":api.url_for(QuestionnaireItem, id = id)})
		
api.add_resource(QuestionnaireItem, "/api/questionnaires/<id>/")	

class QuestionCollection(Resource):
    def get(self, questionnaire_id):
        questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No Questionnaire was found with id {}".format(questionnaire_id))
		
        db_question= Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        items=[]
        for item in db_question:
            question = InventoryBuilder(
                id = item.id,
                questionnaire_id = item.questionnaire_id,
			    title = item.title,
			    description = item.description
			)
            question.add_control("self", "/api/questionnaires/{}/questions/{}/".format(item.questionnaire_id, item.id))
            question.add_control("profile", QUESTION_PROFILE)
            items.append(question)
            
        body = InventoryBuilder(
            items = items
        )
        body.add_namespace("survey", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(QuestionCollection, questionnaire_id = questionnaire_id))
        body.add_control("questionnaire-with", "/api/questionnaires/{}/questions/".format(questionnaire_id))
        body.add_control_add_question(questionnaire_id)
            
        return Response(json.dumps(body), 200, mimetype=MASON)
        
    def post(self, questionnaire_id):
        if not request.json:
            return MasonBuilder.create_error_response(415, "Unsupported media type", "Request must be JSON")
				
        try:
            validate(request.json, MasonBuilder.question_schema(self))
        except ValidationError as e:
            return MasonBuilder.create_error_response(400, "Invalid JSON document", str(e))
		
        questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No Questionnaire with the id {}".format(questionnaire_id))
		
        question_id = ''
        try:
            question = Question(
                questionnaire_id = questionnaire_id,
                title = request.json["title"],
                description = request.json["description"]
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        except KeyError:
            question = Question(
			    questionnaire_id = questionnaire_id,
                title = request.json["title"]
			)
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        return Response(status = 201, headers={"Location":"/api/questionnaires/{}/questions/{}/".format(questionnaire_id, question_id)})

api.add_resource(QuestionCollection, "/api/questionnaires/<questionnaire_id>/questions/")

class QuestionItem(Resource):
    def get(self,questionnaire_id,id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(id, questionnaire_id))
		
        body = InventoryBuilder(
            id = db_question.id,
            questionnaire_id = db_question.questionnaire_id,
            title = db_question.title,
            description = db_question.description
        )
        body.add_namespace("survey", LINK_RELATIONS_URL)
        body.add_control("self","/api/questionnaires/{}/questions/{}/".format(questionnaire_id, id))
        body.add_control("profile", QUESTION_PROFILE)
        body.add_control("collection", api.url_for(QuestionCollection, questionnaire_id = questionnaire_id))
        body.add_control("answer-to", "/api/questionnaires/{}/questions/{}/answers/".format(questionnaire_id, id))
        body.add_control_edit_question(questionnaire_id, id)
        body.add_control_delete_question(questionnaire_id, id)
        
        return Response(json.dumps(body), 200, mimetype = MASON)
        
    def put(self,questionnaire_id,id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(id, questionnaire_id))
			
        if not request.json:
            return MasonBuilder.create_error_response(415, "Unsupported media type", "Request must be JSON")
        try:
            validate(request.json, MasonBuilder.question_schema(self))
        except ValidationError as e:
            return MasonBuilder.create_error_response(400, "Invalid JSON document", str(e))
            
        try:
            db_question.title = request.json["title"]
            db_question.description = request.json["description"]
            db.session.commit()
        except KeyError:
            db_question.title = request.json["title"]
            db.session.commit()
		
        return Response(status = 204, headers={"Location":"/api/questionnaires/{}/questions/{}/".format(questionnaire_id, id)})
		
    def delete(self,questionnaire_id,id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(id, questionnaire_id))
			
        db.session.delete(db_question)
        db.session.commit()
			
        return Response(status = 204, headers={"Location":"/api/questionnaires/{}/questions/{}/".format(questionnaire_id, id)})
		
api.add_resource(QuestionItem, "/api/questionnaires/<questionnaire_id>/questions/<id>/")

class AnswerCollection(Resource):
    def get(self, questionnaire_id, question_id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = question_id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(question_id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(question_id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(question_id, questionnaire_id))
			
        db_answer= Answer.query.filter_by(question_id = question_id).all()
        items=[]
        for item in db_answer:
            answer = InventoryBuilder(
                id = item.id,
                question_id = item.question_id,
			    content = item.content,
			    userName = item.userName
			)
            answer.add_control("self", "/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, item.question_id, item.id))
            answer.add_control("profile", ANSWER_PROFILE)
            items.append(answer)
            
        body = InventoryBuilder(
            items = items
        )
        body.add_namespace("survey", LINK_RELATIONS_URL)
        body.add_control("self", "/api/questionnaires/{}/questions/{}/answers/".format(questionnaire_id, question_id))
        body.add_control("question-with", "/api/questionnaires/{}/questions/{}/".format(questionnaire_id, question_id))
        body.add_control_add_answer(questionnaire_id, question_id)
            
        return Response(json.dumps(body), 200, mimetype=MASON)
	
    def post(self, questionnaire_id, question_id):
        if not request.json:
            return MasonBuilder.create_error_response(415, "Unsupported media type", "Request must be JSON")
				
        try:
            validate(request.json, MasonBuilder.answer_schema(self))
        except ValidationError as e:
            return MasonBuilder.create_error_response(400, "Invalid JSON document", str(e))
		
        questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "Fail to add a Answer to a Questionnaire with the id {}".format(questionnaire_id))
		
        question = Question.query.filter_by(id = question_id).first()
        if question is None:
            return MasonBuilder.create_error_response(405, "Not found", "Fail to add a Answer to a Question with the id {}".format(question_id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(question_id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(question_id, questionnaire_id))
			
        answer_id = ''
        answer = Answer(
            question_id = question_id,
            content = request.json["content"],
            userName = request.json["userName"]
        )
        db.session.add(answer)
        db.session.commit()
        answer_id = answer.id
    
        return Response(status = 201, headers={"Location": "/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, question_id, answer_id)})

api.add_resource(AnswerCollection, "/api/questionnaires/<questionnaire_id>/questions/<question_id>/answers/")

class AnswerItem(Resource):
    def get(self, questionnaire_id, question_id, id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = question_id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(question_id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(question_id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(id, questionnaire_id))
		
        db_answer = Answer.query.filter_by(id = id).first()
        if db_answer is None:
            return MasonBuilder.create_error_response(406, "Not found", "No answer was found with the id {}".format(id))
		
        answers = Answer.query.filter_by(question_id = question_id).all()
        idOfAnswers = []
        for a in answers:
            idOfAnswers.append(a.id)
        if int(id) not in idOfAnswers:
            return MasonBuilder.create_error_response(409, "Do not match", "The answer with id {} does not belong to question {}".format(id, question_id))
		
        body = InventoryBuilder(
            id = db_answer.id,
            question_id = db_answer.question_id,
            content = db_answer.content,
            userName = db_answer.userName
        )
        body.add_namespace("survey", LINK_RELATIONS_URL)
        body.add_control("self","/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, question_id, id))
        body.add_control("profile", ANSWER_PROFILE)
        body.add_control("collection", "/api/questionnaires/{}/questions/{}/answers/".format(questionnaire_id, question_id))
        body.add_control_edit_answer(questionnaire_id, question_id, id)
        body.add_control_delete_answer(questionnaire_id, question_id, id)
        
        return Response(json.dumps(body), 200, mimetype = MASON)
	
    def put(self, questionnaire_id, question_id, id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = question_id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(question_id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(question_id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(id, questionnaire_id))
		
        db_answer = Answer.query.filter_by(id = id).first()
        if db_answer is None:
            return MasonBuilder.create_error_response(406, "Not found", "No answer was found with the id {}".format(id))
		
        answers = Answer.query.filter_by(question_id = question_id).all()
        idOfAnswers = []
        for a in answers:
            idOfAnswers.append(a.id)
        if int(id) not in idOfAnswers:
            return MasonBuilder.create_error_response(409, "Do not match", "The answer with id {} does not belong to question {}".format(id, question_id))
		
        if not request.json:
            return MasonBuilder.create_error_response(415, "Unsupported media type", "Request must be JSON")
        try:
            validate(request.json, MasonBuilder.answer_schema(self))
        except ValidationError as e:
            return MasonBuilder.create_error_response(400, "Invalid JSON document", str(e))
            
        db_answer.content = request.json["content"]
        db_answer.userName = request.json["userName"]
        db.session.commit()
		
        return Response(status = 204, headers={"Location":"/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, question_id, id)})
        
    def delete(self, questionnaire_id, question_id, id):
        db_questionnaire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnaire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No questionnaire was found with the id {}".format(questionnaire_id))
        db_question = Question.query.filter_by(id = question_id).first()
        if db_question is None:
            return MasonBuilder.create_error_response(405, "Not found", "No question was found with the id {}".format(question_id))
		
        questions = Question.query.filter_by(questionnaire_id = questionnaire_id).all()
        idOfQuestions = []
        for q in questions:
            idOfQuestions.append(q.id)
        if int(question_id) not in idOfQuestions:
            return MasonBuilder.create_error_response(408, "Do not match", "The question with id {} does not belong to questionnaire {}".format(id, questionnaire_id))
		
        db_answer = Answer.query.filter_by(id = id).first()
        if db_answer is None:
            return MasonBuilder.create_error_response(406, "Not found", "No answer was found with the id {}".format(id))
        
        answers = Answer.query.filter_by(question_id = question_id).all()
        idOfAnswers = []
        for a in answers:
            idOfAnswers.append(a.id)
        if int(id) not in idOfAnswers:
            return MasonBuilder.create_error_response(409, "Do not match", "The answer with id {} does not belong to question {}".format(id, question_id))
		
        db.session.delete(db_answer)
        db.session.commit()
			
        return Response(status = 204, headers={"Location":"/api/questionnaires/{}/questions/{}/answers/{}/".format(questionnaire_id, question_id, id)})
        
api.add_resource(AnswerItem, "/api/questionnaires/<questionnaire_id>/questions/<question_id>/answers/<id>/")

class AnswerOfUserToQuestionnaire(Resource):
    def get(self, questionnaire_id, userName):
        db_questionnire = Questionnaire.query.filter_by(id = questionnaire_id).first()
        if db_questionnire is None:
            return MasonBuilder.create_error_response(404, "Not found", "No Questionnaire was found with id {}".format(questionnaire_id))
		
        db_answer = Answer.query.filter_by(userName = userName).first()
        if db_answer is None:
            return MasonBuilder.create_error_response(405, "Not found", "No user was found with name {}".format(userName))
		
        questions = []
        answers = Answer.query.filter_by(userName = userName).all()
        for a in answers:
            questions.append(a.question_id)
        
        idOfQuestion=[]
        for q in questions:
            question = Question.query.filter_by(id = q).first()
            idOfQuestionnaire = question.questionnaire_id
            if int(idOfQuestionnaire) == int(questionnaire_id):
                idOfQuestion.append(q)
		
        items=[]
        for index in idOfQuestion:
            item = Answer.query.filter_by(question_id = index).first()
            answer = InventoryBuilder(
                id = item.id,
                question_id = item.question_id,
                content = item.content,
                userName = item.userName
            )
            answer.add_control("self", "/api/questionnaires/{}/answers/{}/".format(questionnaire_id, userName))
            answer.add_control("profile", ANSWER_PROFILE)
            items.append(answer)
			
        body = InventoryBuilder(
			items = items
        )
        body.add_namespace("survey", LINK_RELATIONS_URL)
        body.add_control("self", "/api/questionnaires/{}/answers/{}/".format(questionnaire_id, userName))
		    
        return Response(json.dumps(body), 200, mimetype=MASON)

api.add_resource(AnswerOfUserToQuestionnaire, "/api/questionnaires/<questionnaire_id>/answers/<userName>/")

@app.route("/profiles/questionnaire/")
def profilesforquestionnaire():
	return "", 200

@app.route("/profiles/question/")
def profilesforquestion():
	return "", 200
	
@app.route("/profiles/answer/")
def profilesforanswer():
	return "", 200

@app.route("/profiles/error/")
def profilesforerror():
	return "", 200

@app.route("/survey/link-relations/")
def relations():
	return "", 200