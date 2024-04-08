import boto3
import json
import requests
from botocore.exceptions import ClientError
import logging


class ResourceDetails():
    def __init__(self):
        self.user_tags = {}

    def get_tagged_resources(self):
        try:
            client = boto3.client('resourcegroupstaggingapi')
            raw_all_resources = client.get_resources()
            print(raw_all_resources)
            all_tagged_resource = raw_all_resources['ResourceTagMappingList']
            print(all_tagged_resource)
            return all_tagged_resource
        except Exception as e:
            print(f"Function:get_tagged_resources, Error:{e}")
    def tag_enforcement_1(self, resources):
        try:
            client = boto3.client('resourcegroupstaggingapi')
            for resource in resources:
                resource_arn = resource['ResourceARN']
                tags = resource['Tags']

                print(f"ARN : {resource_arn}")
                print(f"Tags: {tags}")

                tags.append(
                    {'Key'   : 'HackathonTags',
                     'Value' : 'HackathonTagsValue'}
                )
                print(f"Tags : {tags}")

                tag_dict = {tag['Key']:tag['Value'] for tag in tags}

                print(f"Tag Dict : {tag_dict}")

                client.tag_resources(ResourceARNList=[resource_arn], Tags=tag_dict)
                print("Tagging Enforcement is done")
        except Exception as e:
            print(f"Function:tagging_resources, Error:{e}")
    def get_s3_buckets(self):
        try:
            client = boto3.client('s3')
            response = client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets',[]) ]
            return buckets
        except Exception as e:
            print(f"Function:get_s3_buckets, Error:{e}")

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

    def call_leanix(self, res_type, res_id, acct_id):
        print(f"Function: Call LeanIX API")
        url = "http://localhost:5000/tags"
        params = {
            "resource_type": res_type,
            "resource_id": res_id,
            "account_id": acct_id,
        }

        response = requests.get(url, params=params)
        return response.json()

    def load_user_tags(self):
        try:
            with open('user_defined_tags.json', 'r') as file:
                self.user_tags = json.load(file)
        except Exception as e:
            print(f"Error Loading while fetching User Tags from file: Error : {e}")

    def validate_with_mandatory_tags(self,mandatory_tags,s3_tags):
        print(f"Function: validate_with_mandatory_tags")
        final_mandatory_tags = s3_tags.copy()
        for mandatory_tag_key, mandatory_tag_value in mandatory_tags.items():
            for s3_tag in final_mandatory_tags:
                if s3_tag['Key'] == mandatory_tag_key:
                    s3_tag['Value'] = mandatory_tag_value
                    break
            else:
                final_mandatory_tags.append({'Key' : mandatory_tag_key , 'Value' : mandatory_tag_value})
        final_tag_dict = {tag['Key']:tag['Value'] for tag in final_mandatory_tags}
        print(f"Final Tags: {final_tag_dict}")
        return final_tag_dict

    def tagging_enforcement_s3(self):

    def tagging_enforcement(self, res_type, res_id, final_tags):
        print(f"Function: tagging_enforcement : {res_id}")
        if res_type == "s3":
            s3_client = boto3.client('s3')
            tagging = {'TagSet':final_tags}
            s3_client.put_bucket_tagging(Bucket=res_id, Tagging=tagging)
            print(f"Tagging Enforcement for bucket {res_id} has been completed. ")

    def process_resource_type(self,res_type):
        if res_type == "s3":
            obj.s3_processing()


    def get_user_defined_tags(self, res_type,bucket,acct_id):
        obj.load_user_tags()
        try:
            return self.user_tags["user_tags"][res_type][acct_id]
        except Exception as e:
            print(f"Error: No user tags found for {res_type} and {acct_id} : Error_Message : {e}")

    def s3_processing(self):
        s3_buckets = obj.get_s3_buckets()
        if s3_buckets:
            print(f"S3 Buckets Tags Reconciliation")
            for bucket in s3_buckets:
                # Getting buckets Tags
                print(f"Bucket Name : {bucket}")
                s3_tags = obj.get_bucket_tags(bucket)
                print(f"Existing Tags: {s3_tags}")

                # Calling for User Defined Tags
                user_defined_tags = obj.get_user_defined_tags("s3",bucket,"A1")
                print(f"User Tags for bucket {bucket} are : {user_defined_tags}")

                # Calling LeanIX function to get the Mandatory fields
                mandatory_tags = obj.call_leanix("s3", bucket, "A1")
                print(f"Mandatory Tags from LeanIX {mandatory_tags}")

                # Validate if S3 Bucket has all the mandatory tags or not.
                all_mandatory_tags = obj.validate_with_mandatory_tags(mandatory_tags, s3_tags)
                print(f"All Mandatory Tags are : {all_mandatory_tags}")

                #final_tags = user_defined_tags.copy()
                #final_tags.update(all_mandatory_tags)

                final_tags = {**all_mandatory_tags, **user_defined_tags}
                print(f"Final All Mandatory Tags and User Defined Tags : {final_tags}")

                # Final Enforcing the all the mandatory tags to resource
                obj.tagging_enforcement("s3", bucket, final_tags)


if __name__ == "__main__":
    obj = ResourceDetails()
    print("1. S3 Tag Enforcement and Reconciliation\n"
          "2. EC2 Tag Enforcement and Reconciliation\n"
          "3. RDS Tag Enforcement and Reconciliation\n"
          "4. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        obj.process_resource_type("s3")
    elif choice == '2':
        obj.process_resource_type("ec2")
    elif choice == '3':
        obj.process_resource_type("rds")
    else:
        print(f"Invalid Choise, Try Again")














