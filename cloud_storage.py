from google.cloud import storage, exceptions
from google.cloud.storage import Blob

import constants
import json


class CloudStorage:

    def __init__(self):
        self.gcs = storage.Client(project=constants.PROJECT_ID)

    # def check_bucket(self, bucket_name):
    #     try:
    #         self.gcs.get_bucket(bucket_name)
    #         return True
    #     except exceptions.NotFound:
    #         print ('Error: Bucket {} does not exists.'.format(bucket_name))
    #         return False
    #     except exceptions.BadRequest:
    #         print ('Error: Invalid bucket name {}'.format(bucket_name))
    #         return None
    #     except exceptions.Forbidden:
    #         print ('Error: Forbidden, Access denied for bucket {}'.format(bucket_name))
    #         return None

    # def create_bucket(self, capital_record, bucket_name, capital_record_id):
    #     bucket_exists = self.check_bucket(bucket_name)

    #     if bucket_exists is not None:
    #         try:
    #             if not bucket_exists:
    #                 # print ('creating bucket {}'.format(bucket_name))
    #                 # self.gcs.create_bucket(bucket_name)
    #                 return {}, 404

    #             self.store_file_to_gcs(bucket_name, capital_record, capital_record_id)
    #             return True
    #         except Exception as e:
    #             print ("Error: Create bucket Exception")
    #             print (e)
    #             return None
    #     return bucket_exists

    def store_file_to_gcs(self, bucket_name, capital_record, capital_record_id):
        # if self.check_bucket(bucket_name):
        try:
            bucket = self.gcs.get_bucket(bucket_name)
            filename = 'noctilucent_' + str(capital_record_id) + '.json'
            print(filename)
            with open(filename, 'w') as outfile:
                json.dump(capital_record, outfile)
            blob = Blob(filename, bucket)

            try:
                with open(filename, 'rb') as input_file:
                    blob.upload_from_file(input_file)
                return 'Ok', 200
            except IOError as e:
                print (str(e))
                return 'failed to store capital', 404
        except Exception as e:
            print (str(e))
            return 'failed to store', 404



