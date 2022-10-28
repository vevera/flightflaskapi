import sys
import threading
import io

import os



from minio import Minio
from minio.error import S3Error
from minio import datatypes
class S3:
    """
        Class responsible for the AWS S3 integration.
    """
    #resource = aws.resource("s3")
    client = Minio(
        "127.0.0.1:9000",
        access_key="admin",
        secret_key="admin1234",
        secure=False
    )

    @staticmethod
    def create_bucket(username):
        """
        Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param username: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """

        # Create bucket
        # try:
        #     S3.client.make_bucket(f'{username}.s3')
        #     print(f"Creating the {username}\'s storage. Please give a moment to access!")
        # except:
        #     return False

        found = S3.client.bucket_exists(f'{username}.s3')
        if not found:
            S3.client.make_bucket(f'{username}.s3')
        else:
            print("Bucket 'asiatrip' already exists")
        return True

    @staticmethod
    def listing_bucket(username):

        # Retrieve the list of existing buckets
        response = S3.client.list_buckets()
        print(response)
        # Output the bucket names
        # for bucket in response['Buckets']:
        #     if f"{username}.s3" != bucket["Name"]:
        #         pass
        #     else:
        #         return bucket["Name"]

    @staticmethod
    def listing_files(bucket):
        files = S3.client.list_objects(bucket)
        for f in files:
            print(f.object_name)
     
        #print(files)
        # files_list = []
        # for file in files["Contents"]:
        #     files_list.append(file["Key"])
        # return files_list

    @staticmethod
    def batch_upload(path, bucket):

        # Getting Files
        print("Here are all the files in the folder:")
        for file in os.listdir(f"{path}"):
            print(file)
            data = open(f"{path}/{file}", 'rb')

            # Upload
            S3.resource.Bucket(f"{bucket}").put_object(Key=file, Body=data)

        print("All the files were uploaded successfully!")

    @staticmethod
    def upload_to_bucket(name, data, bucket):

        # Getting Files
        #print("Here are all the files in the folder:")
        # for file in os.listdir(f"{path}"):
        #     print(file)
        #     data = open(f"{path}/{file}", 'rb')

            # Upload

        
        stream = io.BytesIO(data)
        S3.client.put_object(bucket, name, stream , length=len(data))
        #S3.resource.Bucket(f"{bucket}").put_object(Key=name, Body=data)

        print("File uploaded!")

    @staticmethod
    def url_from_file(bucket, file):
        # try:
        response = S3.client.presigned_get_object(bucket, file)
        return response
            # Read data from response.
        # finally:
        #     response.close()
        #     response.release_conn()
        # files = S3.listing_files(bucket)
        # for file in files:
        #     filename = f"{path}/" + file
        #     S3.client.download_file(bucket, file, filename, Callback=ProgressPercentage(file, bucket))

        print("\nDownload Successfully!\n")


class ProgressPercentage(object):
    """
      Class responsible for a visual percentage progress line.
    """

    def __init__(self, filename, bucket):
        self._filename = filename
        self._size = S3.client.head_object(Bucket=bucket, Key=filename)['ContentLength']
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (
                self._filename, self._seen_so_far, self._size,
                percentage))
            sys.stdout.flush()
