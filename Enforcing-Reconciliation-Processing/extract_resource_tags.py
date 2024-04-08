import json
import boto3
from botocore.exceptions import ClientError


class ExtractTags():
    def __init__(self):
        print(f"Extraction the existing Tags")

    def get_bucket_tags(self,bucket_name):
        try:
            print(f"Function: get_bucket_tags")
            client = boto3.client('s3')
            response = client.get_bucket_tagging(Bucket=bucket_name)
            bucket_tags = response.get('TagSet',[]) # Needs to handle error if No tags present
            return bucket_tags
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                print(f"No Tags found for the bucket : {bucket_name}")
                return []
            else:
                print(f"Error: Function:get_bucket_tags, Error_Message:{e}")

    def extract_tags(self,res_type):
        if res_type == "s3":
            self.s3_processing(res_type)

    def get_s3_buckets(self):
        try:
            client = boto3.client('s3')
            response = client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets',[]) ]
            return buckets
        except Exception as e:
            print(f"Function:get_s3_buckets, Error:{e}")



    def s3_processing(self,res_type):
        s3_buckets = self.get_s3_buckets()
        if s3_buckets:
            data = {res_type : {}}
            print(f"S3 Buckets Tags Reconciliation")
            for bucket in s3_buckets:

                # Getting S3 buckets Tags
                print(f"Bucket Name : {bucket}")
                s3_tags = self.get_bucket_tags(bucket)
                print(f"Existing Tags: {s3_tags}")

                # Appening Bucket and its Tags
                data[res_type][bucket] = s3_tags

            json_data = json.dumps(data,indent=4)

            # Write JSON data into file
            with open("resources_tags_details.json", "a") as file:
                file.write(json_data)


