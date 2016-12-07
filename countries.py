from datetime import datetime
import copy

from google.cloud import datastore

import constants


class Capitals:

    def __init__(self):
        self.ds = datastore.Client(project=constants.PROJECT_ID)
        self.kind = "Capitals"

    def store_capital(self, rowid, payloadid, country, name, countryCode, continent, latitude, longitude):
        key = self.ds.key(self.kind, rowid)
        entity = datastore.Entity(key)

        entity['id'] = payloadid
        entity['country'] = country
        entity['name'] = name
        entity['countryCode'] = countryCode
        entity['continent'] = continent
        entity['latitude'] = latitude
        entity['longitude'] = longitude              

        return self.ds.put(entity)

    # GET /api/capitals/{id}
    def fetch_capital(self, id):
        return Capitals.nest_geopoint(self.ds.get(self.ds.key(self.kind, int(id))))


    # GET /api/capitals
    def fetch_capitals(self):
        query = self.ds.query(kind=self.kind)
        # query.order = ['-timestamp']
        return [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]

    @staticmethod
    def nest_geopoint(flat):
        nested = copy.deepcopy(flat)
        del nested['latitude']
        del nested['longitude']
        nested['location'] = {'latitude': flat['latitude'], 'longitude': flat['longitude']}
        return nested

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

    def delete_captial(self, id):
        self.ds.delete(self.ds.key("Capitals", id))



