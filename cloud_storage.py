from google.cloud import storage, exceptions
from google.cloud.storage import Blob

import constants
import json


class CloudStorage:

    def __init__(self):
        self.gcs = storage.Client(project=constants.PROJECT_ID)

    def check_bucket(self, bucket_name):
        try:
            self.gcs.get_bucket(bucket_name)
            return True
        except exceptions.NotFound:
            print ('Error: Bucket {} does not exists.'.format(bucket_name))
            return False
        except exceptions.BadRequest:
            print ('Error: Invalid bucket name {}'.format(bucket_name))
            return None
        except exceptions.Forbidden:
            print ('Error: Forbidden, Access denied for bucket {}'.format(bucket_name))
            return None

    def create_bucket(self, capital_record, bucket_name):
        bucket_exists = self.check_bucket(bucket_name)

        if bucket_exists is not None and not bucket_exists:
            try:
                print ('creating bucket {}'.format(bucket_name))
                self.gcs.create_bucket(bucket_name)
                self.store_file_to_gcs(bucket_name, capital_record)
                return True
            except Exception as e:
                print ("Error: Create bucket Exception")
                print (e)
                return None
        return bucket_exists

    def store_file_to_gcs(self, bucket_name, capital_record):
        if self.check_bucket(bucket_name):
            bucket = self.gcs.get_bucket(bucket_name)
            filename = 'data.json'
            with open(filename, 'w') as outfile:
                json.dump(capital_record, outfile)
            blob = Blob(filename, bucket)

            try:
                with open(filename, 'rb') as input_file:
                    blob.upload_from_file(input_file)
                return True
            except IOError:
                print ('Error: Cannot find the file {}'.format(filename))
        return False



