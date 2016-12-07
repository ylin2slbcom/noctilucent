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


geo_point_model = api.model('GeoPoint', {
    'latitude': fields.Float(required=False),
    'longitude': fields.Float(required=False),
    })

capital_mode = api.model('Capital', {
    'id': fields.Integer(required=False),
    'country': fields.String(required=False),
    'name': fields.String(required=False),
    'location': fields.Nested(geo_point_model, required=False),
    'countryCode': fields.String(required=False),
    'continent': fields.String(required=False),
    })


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
    @api.marshal_list_with(capital_mode)
    def get(self):
        return countries.Capitals().fetch_capitals(), 200



@api.route('/api/capitals/<string:id>')
class Capital(Resource):
    @api.marshal_with(capital_mode)
    def get(self, id):
        return countries.Capitals().fetch_capital(id), 200

    @api.expect(capital_mode, validate=True)
    def put(self, id):
            data = {}
            try:
                country_from_input = request.get_json()
                if country_from_input == None:
                    return {}, 400
                
                
                print("hi")
                # obj = request.get_json()['country']
                if 'id' in country_from_input:
                    rowid = country_from_input['id']
                if 'country' in country_from_input:
                    countryName = country_from_input['country']
                if 'name' in country_from_input:
                    name = country_from_input['name']
                if 'countryCode' in country_from_input:
                    countryCode = country_from_input['countryCode']
                if 'continent' in country_from_input:
                    continent = country_from_input['continent']
                if 'location' in country_from_input:
                    location = country_from_input['location']
                print(location)
                print(name)
                capitals = countries.Capitals()
                capitals.store_capital(rowid, countryName, name, countryCode, continent, location)
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
