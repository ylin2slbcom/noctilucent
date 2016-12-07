"""Main Entrypoint for the Application"""

import logging
import json
import base64

from flask import Flask, request, Response
from flask import jsonify
from flask_restplus import Resource, Api, reqparse, fields
from google.cloud import datastore

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
        'insert': True,
        'fetch': False,
        'delete': False,
        'list': False
        }, 200


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
                            
                # print("hi")
                if 'country' in country_from_input:
                    countryName = country_from_input['country']
                if 'name' in country_from_input:
                    name = country_from_input['name']
                if 'countryCode' in country_from_input:
                    countryCode = country_from_input['countryCode']
                if 'continent' in country_from_input:
                    continent = country_from_input['continent']
                if 'location' in country_from_input:
                    latitude = country_from_input['location']['latitude']
                    longitude = country_from_input['location']['longitude']
                # print(name)
                capitals = countries.Capitals()
                capitals.store_capital(id, countryName, name, countryCode, continent, latitude, longitude)
                return "hi", 200

            except Exception as e:
                # swallow up exceptions
                logging.exception('Oops!')

    def delete(self, id):
        try:
            countries.Capitals.delete_captial(id)
            return 200
        except Exception as e:
            logging.exception("Delete failed")

def store_capital_as_string(capital, id): 
    datastore_client = datastore.Client(project=constants.PROJECT_ID) 
    key = datastore_client.key('capital_string', id) 
    entity = datastore_client.get(key) 
    if entity: 
        datastore_client.delete(key) 
     
    entity = datastore.Entity(key) 
    entity['json_string'] = json.dumps(capital) 
    return datastore_client.put(entity) 
 
def retrieve_capital_from_string(id): 
    datastore_client = datastore.Client(project=constants.PROJECT_ID) 
    key = datastore_client.key('capital_string', id) 
    entity = datastore_client.get(key) 
    if not entity: 
        return {} 
    print(entity['json_string']) 
    return json.loads(entity['json_string']) 

def delete_capital_as_string(id):
    datastore_client = datastore.Client(project=constants.PROJECT_ID) 
    key = datastore_client.key('capital_string', id) 
    entity = datastore_client.get(key) 
    if entity: 
        datastore_client.delete(key) 
    

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
