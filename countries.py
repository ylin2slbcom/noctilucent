from datetime import datetime
import copy

from google.cloud import datastore

import constants


class Capitals:

    def __init__(self):
        self.ds = datastore.Client(project=constants.PROJECT_ID)
        self.kind = "Capitals"

    def store_capital(self, rowid, country, name, countryCode, continent, latitude, longitude):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)

        entity['Id'] = rowid
        entity['Country'] = country
        entity['Name'] = name
        entity['CountryCode'] = countryCode
        entity['Continent'] = continent
        entity['Latitude'] = latitude
        entity['Longitude'] = longitude              

        return self.ds.put(entity)

    # GET /api/capitals/{id}
    def fetch_capital(self, id):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', id)
        return Capitals.nest_geopoint(self.get_query_results(query)[0])

    # GET /api/capitals
    def fetch_capitals(self):
        query = self.ds.query(kind=self.kind)
        # query.order = ['-timestamp']
        return [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]

    @staticmethod
    def nest_geopoint(flat):
        nested = copy.deepcopy(flat)
        del nested['Latitude']
        del nested['Longitude']
        nested['location'] = {'latitude': flat['Latitude'], 'longitude': flat['Longitude']}
        return nested

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

