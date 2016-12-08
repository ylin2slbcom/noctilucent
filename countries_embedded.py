from datetime import datetime
import copy

from google.cloud import datastore

import constants


class Capitals:

    def __init__(self):
        self.ds = datastore.Client(project=constants.PROJECT_ID)
        self.kind = "CapitalsEmbedded"

    def store_capital(self, rowid, data):
        key = self.ds.key(self.kind, rowid)
        entity = datastore.Entity(key)
        embedded_key = self.ds.key(self.kind)
        embedded_entity = datastore.Entity(key=embedded_key)
        embedded_entity['id']=data['id']
        embedded_entity['country']=data['country']
        embedded_entity['name']=data['name']
        embedded_entity['countryCode']=data['countryCode']
        embedded_entity['continent']=data['continent']

        embedded_key1 = self.ds.key(self.kind)
        embedded_entity1 = datastore.Entity(key=embedded_key1)
        embedded_entity1['latitude']=data['location']['latitude']
        embedded_entity1['longitude']=data['location']['longitude']

        embedded_entity['location']=embedded_entity1
        entity['countryInfo']=embedded_entity

        return self.ds.put(entity)

    # GET /api/capitals/{id}
    def fetch_capital(self, id):
        return self.ds.get(self.ds.key(self.kind, id)['countryInfo'])

    # GET /api/capitals
    def fetch_capitals(self):
        query = self.ds.query(kind=self.kind)
        # query.order = ['-timestamp']
        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

    def delete_capital(self, id):
        self.ds.delete(self.ds.key(self.kind, id))



