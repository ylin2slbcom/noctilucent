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
        return Capitals.nest_geopoint(self.ds.get(self.ds.key(self.kind, id)))


    # GET /api/capitals
    def fetch_capitals(self):
        query = self.ds.query(kind=self.kind)
        # query.order = ['-timestamp']
        return [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]

    # should be static or class or something, but whatever...
    def get_by_id(self, id):
        return self.ds.get(self.ds.key(self.kind, id))

    @staticmethod
    def nest_geopoint(flat):
        # nested = copy.deepcopy(flat)
        # del nested['latitude']
        # del nested['longitude']
        nested = {key: flat[key] for key in flat if key not in ('latitude', 'longitude')}
        nested['location'] = {'latitude': flat['latitude'], 'longitude': flat['longitude']}
        return nested

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

    def delete_capital(self, id):
        self.ds.delete(self.ds.key(self.kind, id))

    def query_capital(self, qeury_key, query_value):
        filter_value = [(qeury_key, '=', query_value)]
        query = self.ds.query(kind=self.kind, filters=filter_value)
        return [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]

    def search_captial(self, query_value):
        capitals = []
        query = self.ds.query(kind=self.kind)
        new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        capitals.extend(new_capitals)

        # filter_value = [('id', '=', query_value)]
        # query = self.ds.query(kind=self.kind, filters=filter_value)
        # new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        # capitals.extend(new_capitals)

        filter_value = [('country', '>=', query_value)]
        query = self.ds.query(kind=self.kind, filters=filter_value)
        new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        capitals.extend(new_capitals)

        filter_value = [('name', '>=', query_value)]
        query = self.ds.query(kind=self.kind, filters=filter_value)
        new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        capitals.extend(new_capitals)

        filter_value = [('countryCode', '>=', query_value)]
        query = self.ds.query(kind=self.kind, filters=filter_value)
        new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        capitals.extend(new_capitals)

        filter_value = [('continent', '>=', query_value)]
        query = self.ds.query(kind=self.kind, filters=filter_value)
        new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        capitals.extend(new_capitals)

        # filter_value = [('latitude', '>=', query_value)]
        # query = self.ds.query(kind=self.kind, filters=filter_value)
        # new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        # capitals.extend(new_capitals)

        # filter_value = [('longitude', '>=', query_value)]
        # query = self.ds.query(kind=self.kind, filters=filter_value)
        # new_capitals = [Capitals.nest_geopoint(x) for x in self.get_query_results(query)]
        # capitals.extend(new_capitals)

        return capitals



