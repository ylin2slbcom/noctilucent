"""Main Entrypoint for the Application"""
from __future__ import print_function

import logging
import json
import base64

from flask import Flask, request, Response, render_template
from flask import jsonify
from flask_restplus import Resource, Api, reqparse, fields
from google.cloud import datastore
from google.cloud import pubsub
from google.cloud import storage

import utility
from flask import Blueprint

import constants
import countries
import cloud_storage


api = Blueprint('capitals', __name__)

app = Flask(__name__)
api = Api(app, version='1.0', title=constants.TEAM_NAME)


geo_point_model = api.model('GeoPoint', {
    'latitude': fields.Float(required=False),
    'longitude': fields.Float(required=False),
    })

capital_model = api.model('Capital', {
    'id': fields.Integer(required=False),
    'country': fields.String(required=False),
    'name': fields.String(required=False),
    'location': fields.Nested(geo_point_model, required=False),
    'countryCode': fields.String(required=False),
    'continent': fields.String(required=False),
    })

capitals_request_parser = reqparse.RequestParser(bundle_errors=True)
capitals_request_parser.add_argument('query', type=str, required=False)
capitals_request_parser.add_argument('search', type=str, required=False)

storage_request_parser = reqparse.RequestParser(bundle_errors=True)
storage_request_parser.add_argument('bucket', type=str, required=False)


storage_model = api.model('Bucket', {
    'bucket': fields.String(required=True),
    })
topic_model = api.model('Topic', {
    'topic': fields.String(required=False),
    })


@api.route('/api/status')
class status(Resource):
    def get(self):
        return {
        'insert': True,
        'fetch': True,
        'delete': True,
        'list': True,
        'query': True,
        'search': True,
        'pubsub': True,
        'storage': True
        }, 200


@api.route('/api/capitals')
class Capitals(Resource):
    @api.marshal_list_with(capital_model)
    @api.expect(capitals_request_parser, validate=True)
    def get(self):
            args = capitals_request_parser.parse_args()
            query_string = args['query']
            search_string = args['search']
            if search_string is not None:
                capitals = countries.Capitals().search_captial(search_string)
                if len(capitals) < 1:
                    return [], 404
                return capitals, 200
            
            if query_string is not None:
                splitted_query_string = query_string.split(':')
                if len(splitted_query_string) != 2:
                    return 'wrong query format', 400
                
                return countries.Capitals().query_capital(splitted_query_string[0], splitted_query_string[1]), 200                
            return countries.Capitals().fetch_capitals(), 200
    


@api.route('/api/capitals/<int:id>/publish')
class Publish(Resource):
    @api.expect(topic_model, validate=True)
    def post(self, id):
        try:
            capital = countries.Capitals().get_by_id(id)
            logging.info('badaboom::capital is {}'.format(capital))####
            print('badaboom::capital is {}'.format(capital))####
            if capital is None:
                logging.info('badaboom::capital not found')####
                print('badaboom::capital not found')####
                return {"code": 0,  "message": "capital not found"}, 404
            topic_name = request.get_json()['topic']
            meow = topic_name.split('/')
            pubsub_client = pubsub.Client(meow[1])
            print('badaboom::nyaaa? {}'.format(meow[1]))####
            logging.info('badaboom::nyaaa? {}'.format(meow[1]))####
            topic_name = meow[3]
            print('badaboom::topic name is {}'.format(topic_name))####
            logging.info('badaboom::topic name is {}'.format(topic_name))####
#            print(topic_name)
            topic = pubsub_client.topic(topic_name)
#            print('ok...')
            #topic.create() #... don't create a topic, you misunderstand =/...
#            print('yeah??')
#            return {}, 200  ### no need to return right?
            try:
                topic.create()
                print('badaboom::topic created!!!')
                logging.info('badaboom::topic created!!!')
            except:
                logging.info('probably topic {} already exists'.format(topic_name))
                print('probably topic {} already exists'.format(topic_name))
            logging.info('publishing... {}'.format(json.dumps(countries.Capitals.nest_geopoint(capital))))
            print('publishing... {}'.format(json.dumps(countries.Capitals.nest_geopoint(capital))))
            return_shi =  {"messageId": int(topic.publish(json.dumps(countries.Capitals.nest_geopoint(capital))))}, 200
            logging.info('returned shi is {}'.format(return_shi))
            print('returned shi is {}'.format(return_shi))
            return return_shi
        except:
            logging.exception("something went wrong, maybe already existing with this name not consumed?")
            print("something went wrong, maybe already existing with this name not consumed?")
            return {"code": 0,  "message": "something went wrong, maybe already existing with this name not consumed?"}, 404  # should be some other error?
        

        

@api.route('/api/capitals/<int:id>')
class Capital(Resource):
    @api.marshal_with(capital_model)
    def get(self, id):
        try:
            results = countries.Capitals().fetch_capital(id)
            if results is None:
                return 'record not found', 404
            return results, 200
        except Exception as e:
            logging.exception(e)
            return 'failed to fetch record', 404

    @api.expect(capital_model, validate=True)
    def put(self, id):
            data = {}
            try:
                country_from_input = request.get_json()
                if country_from_input == None:
                    return {}, 400
                            
                # print("hi")
                if 'id' in country_from_input:
                    payloadid = country_from_input['id']
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
                    if location is not None:
                        if 'latitude' in location:
                            latitude = location['latitude']
                        if 'longitude' in location:
                            longitude = location['longitude']
                # print(name)
                capitals = countries.Capitals()
                capitals.store_capital(id, payloadid, countryName, name, countryCode, continent, latitude, longitude)
                return "hi", 200

            except Exception as e:
                # swallow up exceptions
                logging.exception('Oops!')

    def delete(self, id):
        try:
            countries.Capitals().delete_capital(id)
            return 'ok', 200
        except Exception as e:
            logging.exception("Delete failed")
            return 'failed to delete', 404
            
            
@api.route('/api/capitals/<int:id>/store')
class Store(Resource):
    @api.expect(storage_request_parser)
    def get(self, id):
        try:
            args = storage_request_parser.parse_args()
            bucket_name = args['bucket']
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            results = []
            blobs = bucket.list_blobs()
            if blobs is not None:
                for blob in blobs:
                    results.append(blob.name)
                
            return str(results), 200
        except Exception as e:
            return str(e), 404
        
    
    @api.expect(storage_model, validate=True)
    def post(self, id):
        data = {}
        try:
            bucket_info = request.get_json()
            if bucket_info == None:
                return {}, 400
                        
            if 'bucket' in bucket_info:
                bucket_name = bucket_info['bucket']
            
            capital_record = countries.Capitals().fetch_capital(id)
            gcs = cloud_storage.CloudStorage()
            # gcs.create_bucket(capital_record, bucket_name, id)
            mesg, code = gcs.store_file_to_gcs(bucket_name, json.dumps(capital_record), id)
            return mesg, code

        except Exception as e:
            # swallow up exceptions
            logging.exception('Oops!')        
            return 'failed to store capital', 404
        

@app.route('/list')
def list():
    caps_w_dups = countries.Capitals().fetch_capitals()
    caps_wo_dups = sorted(set((cap['country'], cap['name']) for cap in caps_w_dups))
    return render_template('welcome.html', capitals=caps_wo_dups)


@app.route('/google_map')
def google_map():
    caps_w_dups = countries.Capitals().fetch_capitals()
    caps_wo_dups = set((cap['location']['latitude'], cap['location']['longitude']) for cap in caps_w_dups)
    return render_template('google_map.html', lat_longs=caps_wo_dups)


@app.route('/polymer')
def polymer_map():
    caps_w_dups = countries.Capitals().fetch_capitals()
    caps_wo_dups = set((cap['location']['latitude'], cap['location']['longitude'], cap['country'], cap['name']) for cap in caps_w_dups)
    return render_template('index.html', lat_longs=caps_wo_dups)

@app.route('/polymer/<string:map_lat>/<string:map_lng>')
def polymer_mapll(map_lat, map_lng):
    caps_w_dups = countries.Capitals().fetch_capitals()
    caps_wo_dups = set((cap['location']['latitude'], cap['location']['longitude'], cap['country'], cap['name']) for cap in caps_w_dups)
    return render_template('index.html', map_lat=map_lat, map_lng=map_lng, lat_longs=caps_wo_dups)

@app.route('/polymer/<string:map_lat>/<string:map_lng>/<string:start>')
def polymer_map1(map_lat, map_lng, start):
    caps_w_dups = countries.Capitals().fetch_capitals()
    caps_wo_dups = set((cap['location']['latitude'], cap['location']['longitude'], cap['country'], cap['name']) for cap in caps_w_dups)
    return render_template('index.html', lat_longs=caps_wo_dups, map_lat=map_lat, map_lng=map_lng, start=start)

@app.route('/polymer/<string:map_lat>/<string:map_lng>/<string:start>/<string:end>')
def polymer_map2(map_lat, map_lng, start, end):
    caps_w_dups = countries.Capitals().fetch_capitals()
    caps_wo_dups = set((cap['location']['latitude'], cap['location']['longitude'], cap['country'], cap['name']) for cap in caps_w_dups)
    return render_template('index.html', lat_longs=caps_wo_dups, map_lat=map_lat, map_lng=map_lng, start=start, end=end)

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
    app.run(host='127.0.0.1', port=8080, debug=True, use_reloader=False, use_evalex=False)

