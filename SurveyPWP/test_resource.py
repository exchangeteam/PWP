import json
import os
import pytest
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
from app import app,db, Questionnaire, Question, Answer

@pytest.fixture
def client():
    """
    This function is making a preparation before testing.
	Before every test that has 'db_handle' as its parmeter, this function will run.
	Thus, every test will have a individual temporary database.
	Code adapted from 'After Exercise 3': Testing Flask Application
    """
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    db.create_all()
    _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """
    Pre-populate database with 1 questionnaire, 3 questions and 3 answers.
    """
    _questionnaire = Questionnaire(
        title="test-questionnaire-1",
        description="test-questionnaire"
    )
    db.session.add(_questionnaire)
    for i in range(1, 3):
        q = Question(
            title = "test-question-{}".format(i),
            description = "test-question",
            questionnaire = _questionnaire
        )
        a = Answer(
            userName = "test-user-{}".format(i),
            content = "test-answer",
            question = q
        )
        db.session.add(q)
        db.session.add(a)
    db.session.commit()

def _check_namespace(client, response):
    """
    Checks that the "survey" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """
    
    ns_href = response["@namespaces"]["survey"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_delete_method(ctrl, client, obj):

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

def _get_questionnaire_json(number=1):
    return {"title": "test-questionnaire-{}".format(number), "description": "test-questionnaire"}

def _get_question_json(number=1):
    return {"title": "test-question-{}".format(number), "description": "test-question"}

def _check_control_put_method(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_sensor_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    

def _check_control_post_method(ctrl, client, obj):
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_questionnaire_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

class TestQuestionnaireCollection(object):
    """
    This class implements tests for each HTTP method in questionnaire collection
    resource. 
    """
    RESOURCE_URL = "/api/questionnaires/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # _check_namespace(client, body)
        _check_control_post_method("survey:add-questionnaire", client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "title" in item
            assert "description" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        valid = _get_questionnaire_json()

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["title"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == "test-questionnaire-1"
        assert body["description"] == "test-questionnaire"

        # test with wrong content type 
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestQuestionnaireItem(object):
    RESOURCE_URL = "/api/questionnaires/1/"
    INVALID_URL = "/api/quesitonnaires/-1/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == "test-questionnaire-1"
        assert body["description"] == "test-questionnaire"
        # _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body)
        _check_control_delete_method("survey:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
            
    def test_put(self,client):
        """Test for valid PUT method"""
        valid = _get_questionnaire_json()

        # test with valid
        resp = client.put(self.RESOURCE_URL,json=valid)
        assert resp.status_code == 204

        # test with another url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 409

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_sensor_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == valid["title"] and body["description"] == valid["description"]

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        


class TestQuestionsByQuestionnaire(object):
    RESOURCE_URL = "/api/questionnaire/1/questions/"
    INVALID_URL = "/api/questionnaire/-1/questions/"

    def test_get(self,client):
        """Tests for questions by questionnaire GET method."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # _check_namespace(client, body)
        _check_control_post_method("survey:add-question", client, body)
        assert len(body["items"]) == 3
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "title" in item
            assert "description" in item

    def test_post(self, client): 
        valid = _get_question_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["title"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == "test-question-1"
        assert body["description"] == "test-question"

        # test with invalid url
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # remove field title for 400
        valid = _get_sensor_json()
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestQuestionItem(object):
    RESOURCE_URL = "/api/questionnaires/1/question/1/"
    INVALID_URL = "/api/quesitonnaires/1/question/-1/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "title" in body["item"]
        assert "description" in body["item"]
        # _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body)
        _check_control_delete_method("survey:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert status_code == 404
            
    def test_put(self,client):
        """Test for valid PUT method"""
        valid = _get_question_json()

        # test with valid
        resp = client.put(self.RESOURCE_URL,json=valid)
        assert resp.status_code == 204

        # test with another url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 409

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_sensor_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == valid["title"] and body["description"] == valid["description"]

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the question afterwards results in 404.
        Also checks that trying to delete a question that doesn't exist results
        in 404.
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestAnswersToQuestion(object):
    RESOURCE_URL = "/api/questionnaire/1/questions/1/answers/"
    INVALID_URL = "/api/questionnaire/1/questions/-1/answers/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # _check_namespace(client, body)
        _check_control_post_method("survey:add-answer", client, body)
        assert len(body["items"]) == 3
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "title" in item
            assert "description" in item

    def test_post(self, client): 
        valid = _get_question_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["title"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == "test-question-1"
        assert body["description"] == "new-question"

        # test with invalid url
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # remove field title for 400
        valid = _get_sensor_json()
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestAnswerItem(object):
    RESOURCE_URL = "/api/questionnaires/1/question/1/answers/1/"
    INVALID_URL = "/api/quesitonnaires/1/question/1/answers/-1/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "title" in body["item"]
        assert "description" in body["item"]
        # _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body)
        _check_control_delete_method("survey:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert status_code == 404
            
    def test_put(self,client):
        """Test for valid PUT method"""
        valid = _get_question_json()

        # test with valid
        resp = client.put(self.RESOURCE_URL,json=valid)
        assert resp.status_code == 204

        # test with another url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 409

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field for 400
        valid.pop("userName")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _get_qeustion_json()
        valid.pop("content")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_sensor_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["userName"] == valid["userName"] and body["content"] == valid["content"]

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the question afterwards results in 404.
        Also checks that trying to delete a question that doesn't exist results
        in 404.
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404