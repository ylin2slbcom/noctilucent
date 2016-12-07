from datetime import datetime
from google.cloud import datastore

import constants


class Capitals:

    def __init__(self):
        self.ds = datastore.Client(project=constants.PROJECT_ID)
        self.kind = "Capitals"

    def store_capital(self, rowid, country, name, countryCode, continent, location):
    def delete_captial(self, key):
        entity = self.fetch_capital(key)
        if entity is not None:
            entity.key.delete()

        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)

        entity['Id'] = rowid
        entity['Country'] = country
        entity['Name'] = name
        entity['CountryCode'] = countryCode
        entity['Continent'] = continent
        # entity['Location'] = location              

        return self.ds.put(entity)

    # GET /api/capitals/{id}
    def fetch_capital(self, id):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', id)
        return self.get_query_results(query)[0]

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

