from datetime import datetime
from google.cloud import datastore


class Capitals:

    def __init__(self):
        self.ds = datastore.Client(project="hackathon-team-002")
        self.kind = "Capitals"

    def store_capital(self, country):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)

        entity['country'] = country

        return self.ds.put(entity)

    def fetch_greetings(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['-timestamp']
        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

