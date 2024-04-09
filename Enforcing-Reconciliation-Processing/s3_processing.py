import boto3
import json
import requests
from botocore.exceptions import ClientError
import logging
import os


class S3Processing():
    def __init__(self):
        self.user_tags = {}

    def get_s3_functions_with_tags(self):
        print(f"\nCalling Function:get_s3_functions_with_tags ")
        try:
            s3_buckets_with_tags = []
            client = boto3.client('s3')
            response = client.list_buckets()

            for bucket in response.get('Buckets',[]):
                bucket_name = bucket['Name']
                tagsCall = client.get_bucket_tagging(Bucket=bucket_name)
                bucket_tags = tagsCall.get('TagSet', [])
                s3_buckets_with_tags.append((bucket_name,bucket_tags))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                print(f"No Tags found for the bucket : {bucket_name}")
                s3_buckets_with_tags.append((bucket_name, {}))
        except Exception as e:
            print(f"Function:get_s3_buckets, Error:{e}")

        return s3_buckets_with_tags

    def call_leanix(self, res_type, acct_id):
        print(f"\nCalling Function:call_leanix ")
        try:
            url = "http://localhost:5000/tags"
            params = {
                "resource_type": res_type,
                "account_id": acct_id,
            }

            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"Error Message : {e}")

    def load_user_tags(self):
        try:
            with open('user_defined_tags.json', 'r') as file:
                self.user_tags = json.load(file)
        except Exception as e:
            print(f"Error Loading while fetching User Tags from file: Error : {e}")

    def validate_with_leanix_tags(self, leanIX_tags, resource_tags):
        print(f"\nCalling Function:validate_with_leanix_tags ")
        try:
            ix_tags = resource_tags.copy()
            for ix_key, ix_val in leanIX_tags.items():
                for resource_tags in ix_tags:
                    if resource_tags['Key'] == ix_key:
                        resource_tags['Value'] = ix_val
                        break
                else:
                    ix_tags.append({'Key' : ix_key , 'Value' : ix_val})

            # Converting List type into Dictionary type
            aggregated_tags = {tag['Key']:tag['Value'] for tag in ix_tags}
            print(f"Final Tags: {aggregated_tags}")

            return aggregated_tags
        except Exception as e:
            print(f"Error Message : {e}")

    def tagging_reconciliation_s3(self, res_id, final_tags):
        print(f"\nCalling Function:tagging_reconciliation_s3 ")
        try:
            client = boto3.client('s3')
            tagging = {'TagSet': final_tags}
            client.put_bucket_tagging(Bucket=res_id, Tagging=tagging)
            print(f"Tagging Enforcement for bucket {res_id} has been completed. \n")
        except Exception as e:
            print(f"Error Message: {e}")



    def get_user_defined_tags(self, res_type,acct_id):
        print(f"\nCalling Function:get_user_defined_tags ")
        try:
            self.load_user_tags()
            return self.user_tags["user_tags"][res_type][acct_id]
        except Exception as e:
            print(f"Error: No user tags found for {res_type} and {acct_id} : Error_Message : {e}")

    def display_dash(self,num):
        print(num*"-")


    def generate_report(self,res_type,bucket):
        print(f"Calling Function: generate_report")
        try:
            filePath = "Reports/Complient_Resources_Report.json"

            if os.path.exists(filePath):
                with open("Reports/Complient_Resources_Report.json", "r") as file:
                    report = json.load(file)
            else:
                report = {}


            if res_type in report:
                report[res_type][bucket] = "Complient"
            else:
                report[res_type] = {bucket:"Complient"}

            json_str = json.dumps(report,indent=4)

            with open("Reports/Complient_Resources_Report.json","w") as file:
                file.write(json_str)

            file.close()
            print(f"Report has been generated")
        except Exception as e:
            print(f"Error Message : {e}")



    def s3_processing(self,res_type):
        try:
            self.display_dash(100)
            print(f"S3 Bucket Processing")
            self.display_dash(100)

            # Getting User Defined Tags
            user_defined_tags = self.get_user_defined_tags(res_type, "A1")
            print(f"User defined Tags for S3 buckets are : {user_defined_tags}")

            # Getting LeanIX Automation-Tags
            leanix_tags = self.call_leanix("s3", "A1")
            print(f"LeanIX Automation Provided Tags: {leanix_tags}")

            # Get S3 Buckets and tags associated with it
            cnt = 0
            s3_buckets_with_tags = self.get_s3_functions_with_tags()
            for bucket,s3_tags in s3_buckets_with_tags:
                print(f"Bucket Name: {bucket}")

                # Validate if S3 Bucket has all the LeanIX tags or not.
                aggregated_s3ix_tags = self.validate_with_leanix_tags(leanix_tags, s3_tags)
                print(f"All Existing & Automation Tags: {aggregated_s3ix_tags}")

                all_tags = {**aggregated_s3ix_tags, **user_defined_tags}

                # Converting Dictionary type into List type
                final_tags = [{'Key':key, 'Value':value} for key,value in all_tags.items()]
                print(f"All Existing,User-defined & Automated Tags: {final_tags}")

                # Final Enforcing the all the mandatory tags to resource
                self.tagging_reconciliation_s3(bucket, final_tags)
                cnt += 1
                self.generate_report(res_type,bucket)
                self.display_dash(100)

            print(f"\nNumber of S3 Buckets Processed : {cnt}\n")
        except Exception as e:
            print(f"Error Message : {e}")




















