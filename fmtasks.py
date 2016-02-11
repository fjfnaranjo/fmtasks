"""
fmtasks's Flask application module.

This module implements a simple RESTful API to manage a list of tasks using
basic CRUD operations. It uses Flask for the API and MongoDB for the storage.
"""


from argparse import ArgumentParser
from os import environ

from flask import Flask, request, url_for
from flask.json import jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId


# General Flask configuration
DEBUG = True
SECRET_KEY = 'development key'

# MongoDB fixed configuration
MONGODB_DATABASE = 'fmtasks'
MONGODB_COLLECTION = 'tasks'
MONGODB_TIMEOUT = 3000
MONGODB_TIMEOUT_EXTRA = 2000

# MongoDB URI configurable using environment
MONGODB_URI = "mongodb://localhost:27017/"
if 'MONGODB_URI' in environ and environ['MONGODB_URI']:
    MONGODB_URI = environ['MONGODB_URI']

# Define Flask app
app = Flask(__name__)
app.config.from_object(__name__)


def get_db_collection():
    """
    Creates the MongoDB lazy connection object.

    It is a simple MongoDB init chain with configurable timeouts.
    """

    client = MongoClient(
        app.config['MONGODB_URI'],
        connectTimeoutMS=app.config['MONGODB_TIMEOUT'],
        serverSelectionTimeoutMS=(
            app.config['MONGODB_TIMEOUT']+app.config['MONGODB_TIMEOUT_EXTRA']
        ),
    )
    db = client[app.config['MONGODB_DATABASE']]
    collection = db[app.config['MONGODB_COLLECTION']]
    return collection


class InvalidAPIUsage(Exception):
    """Exception for invalid API requests."""

    status_code = 400

    def __init__(self, errormsg, status_code=None):
        Exception.__init__(self)
        self.errormsg = errormsg
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(errormsg=self.errormsg)


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    """Error handler for InvalidUsage."""

    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def get_content_or_400(a_request):
    """Checks if a request have a JSON encoded 'content' field."""

    request_json = request.get_json()
    if not request_json or 'content' not in request_json:
        raise InvalidAPIUsage("content is required")
    return request_json['content']


def get_task_or_404(collection, id):
    """Get object or 404 adapted for tasks."""

    object_id = ObjectId(id)
    object = collection.find({"_id": object_id})
    if not object.count():
        raise InvalidAPIUsage("task doesn\'t exists", 404)

    return object[0]


@app.route('/')
def index():
    """The API root path returns a empty response."""

    return jsonify()


@app.route('/task/', methods=['POST'], defaults={'id': None})
@app.route('/task/<id>', methods=['POST'])
def add_task(id):
    """Adds a new task to the database."""

    content = get_content_or_400(request)

    collection = get_db_collection()

    object_id = None
    if id:
        object_id = ObjectId(id)
        object = collection.find({"_id": object_id})
        if object:
            response = jsonify(errormsg="id already exists")
            response.status_code = 400
            return response

    new_object = {"content": content}
    if id:
        new_object["_id"] = id
    new_object_id = collection.insert_one(new_object).inserted_id

    response = jsonify(id=str(new_object_id))
    response.status_code = 201
    response.headers["Location"] = url_for('get_task', id=new_object_id)
    return response


@app.route('/task/', methods=['GET'], defaults={'id': None})
@app.route('/task/<id>', methods=['GET'])
def get_task(id):
    """Get a task from the database."""

    if not id:
        raise InvalidAPIUsage("id is required")

    collection = get_db_collection()

    task = get_task_or_404(collection, id)

    response = jsonify(content=task['content'])
    response.status_code = 200
    return response


@app.route('/task/', methods=['PUT'], defaults={'id': None})
@app.route('/task/<id>', methods=['PUT'])
def edit_task(id):
    """Edit an existing task contents."""

    if not id:
        raise InvalidAPIUsage("id is required")

    content = get_content_or_400(request)

    collection = get_db_collection()

    task = get_task_or_404(collection, id)

    collection.update_one({"_id": task["_id"]}, {"$set": {"content": content}})

    response = jsonify()
    response.status_code = 200
    return response


@app.route('/task/', methods=['DELETE'], defaults={'id': None})
@app.route('/task/<id>', methods=['DELETE'])
def remove_task(id):
    """Edit an existing task contents."""

    if not id:
        raise InvalidAPIUsage("id is required")

    collection = get_db_collection()

    task = get_task_or_404(collection, id)

    collection.delete_one({"_id": task["_id"]})

    response = jsonify()
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0")
