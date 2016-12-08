from google.cloud import storage, exceptions
from google.cloud.storage import Blob

import constants
import json


class CloudStorage:

    def __init__(self):
        self.gcs = storage.Client()

    def store_file_to_gcs(self, bucket_name, capital_record, capital_record_id):
        # if self.check_bucket(bucket_name):
        try:
#             bucket = self.gcs.get_bucket(bucket_name)
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)

            filename = str(capital_record_id)
            blob = bucket.blob(filename)

            try:
                blob.upload_from_string(capital_record, client=self.gcs)
                return 'Ok', 200
            except IOError as e:
                print (str(e))
                return 'failed to store capital', 404
        except Exception as e:
            print (str(e))
            return 'failed to store', 404



