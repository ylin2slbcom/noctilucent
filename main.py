"""Main Entrypoint for the Application"""

import logging
import json
import base64

from flask import Flask, request, Response
from flask import jsonify
from flask_restplus import Resource, Api, reqparse, fields


import utility
from flask import Blueprint

import constants
import countries


api = Blueprint('capitals', __name__)

app = Flask(__name__)
api = Api(app, version='1.0', title=constants.TEAM_NAME)



@api.route('/api/status')
class status(Resource):
    def get(self):
        return {
        'insert': False,
        'fetch': False,
        'delete': False,
        'list': False
        }, 200
        #return constants.TEAM_NAME+'  is running!'


@api.route('/api/capitals')
class Capitals(Resource):
    def get(self):
        return countries.Capitals().fetch_capitals(), 200



@api.route('/api/capitals/<string:id>')
class Capital(Resource):
    def get(self, id):
        return countries.Capitals().fetch_capital(id), 200

    def put(self, id):
            data = {}
            try:
                print("hi")
                # obj = request.get_json()['country']
                countryName = request.get_json()['country']
                name = request.get_json()['name']
                countryCode = request.get_json()['countryCode']
                continent = request.get_json()['continent']
                print(countryName)
                print(name)
                capitals = countries.Capitals()
                # data = base64.b64decode(obj['country'])
                capitals.store_capital(countryName, name, countryCode, continent)
                # data = base64.b64decode(obj['message']['data'])
                # utility.log_info(data)
                # ret
                return "hi", 200

            except Exception as e:
                # swallow up exceptions
                logging.exception('Oops!')

                # pass

    # def delete(self, id):
    #     pass


@app.errorhandler(500)
def server_error(err):
    """Error handler"""
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(err), 500


if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
