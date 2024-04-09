import boto3
import json
import requests
from botocore.exceptions import ClientError
from s3_processing import S3Processing
from lambda_processing import LambdaProcessing
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
    def get_s3_functions_with_tags(self):
        try:
            s3_buckets_with_tags = []
            client = boto3.client('s3')
            response = client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets',[]) ]

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

    def get_lambda_functions_with_tags(self):
        try:
            lambda_function_with_tags = []
            client = boto3.client('lambda')
            funcCall = client.list_functions()
            for func in funcCall['Functions']:
                # Extract Function Name and Function ARN value
                funcName, funcARN = func['FunctionName'], func['FunctionArn']

                # Extract Tags value associated with Function ARN
                tagCall = client.list_tags(Resource=funcARN)
                tags = tagCall.get('Tags',{})
                # Appending function name and tags in the empty list
                lambda_function_with_tags.append((funcName,funcARN,tags))
            return lambda_function_with_tags
        except Exception as e:
            print(f"Function:get_lambda_functions, Error:{e}")


    def call_leanix(self, res_type, acct_id):
        print(f"Function: Call LeanIX API")
        url = "http://localhost:5000/tags"
        params = {
            "resource_type": res_type,
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

    def validate_with_leanix_tags(self, leanIX_tags, resource_tags):
        print(f"Function: validate_with_leanix_tags")
        print(f"A201 : Resource Tags: {resource_tags}")
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

    def tagging_reconciliation_s3(self, res_id, final_tags):
        client = boto3.client('s3')
        tagging = {'TagSet': final_tags}
        client.put_bucket_tagging(Bucket=res_id, Tagging=tagging)
        print(f"Tagging Enforcement for bucket {res_id} has been completed. \n")

    def tagging_reconciliation_lambda(self, res_id, final_tags):
        client = boto3.client('lambda')
        tagging = {'Tags': final_tags}
        client.tag_resource(Resource=res_id, Tags=tagging)
        print(f"Tagging Enforcement for Lambda {res_id} has been completed. ")





    def process_resource_type(self,res_type):
        if res_type == "s3":
            obj.s3_processing(res_type)
        elif res_type == "lambda":
            obj.lambda_processing(res_type)


    def get_user_defined_tags(self, res_type,acct_id):
        obj.load_user_tags()
        try:
            return self.user_tags["user_tags"][res_type][acct_id]
        except Exception as e:
            print(f"Error: No user tags found for {res_type} and {acct_id} : Error_Message : {e}")

    def s3_processing(self,res_type):
        print(f"S3 Bucket Processing")

        # Getting User Defined Tags
        user_defined_tags = obj.get_user_defined_tags(res_type, "A1")
        print(f"User defined Tags for S3 buckets are : {user_defined_tags}")

        # Getting LeanIX Automation-Tags
        leanix_tags = obj.call_leanix("s3", "A1")
        print(f"LeanIX Automation Provided Tags: {leanix_tags}")

        # Get S3 Buckets and tags associated with it
        cnt = 0
        s3_buckets = obj.get_s3_functions_with_tags()
        for bucket,s3_tags in s3_buckets:
            # Getting S3 buckets Tags
            #s3_tags = obj.get_bucket_tags(bucket)

            # Validate if S3 Bucket has all the LeanIX tags or not.
            aggregated_s3ix_tags = obj.validate_with_leanix_tags(leanix_tags, s3_tags)
            print(f"All Mandatory Tags are : {aggregated_s3ix_tags}")

            all_tags = {**aggregated_s3ix_tags, **user_defined_tags}

            # Converting Dictionary type into List type
            final_tags = [{'Key':key, 'Value':value} for key,value in all_tags.items()]
            print(f"All User and Automated Tags are : {final_tags}")

            # Final Enforcing the all the mandatory tags to resource
            obj.tagging_reconciliation_s3(bucket, final_tags)

    def lambda_processing(self,res_type):
        print(f"Lambda Processing")

        # Getting User Defined Tags
        user_defined_tags = obj.get_user_defined_tags(res_type, "B1")
        print(f"User defined Tags for Lambda Functions are : {user_defined_tags}")

        # Getting LeanIX Automation-Tags
        leanix_tags = obj.call_leanix(res_type, "B1")
        print(f"LeanIX Automation Provided Tags: {leanix_tags}")

        # Get Lambda functions and tags associated with it
        cnt = 0
        l_functions = obj.get_lambda_functions_with_tags()
        for funcName, funcARN, l_tags in l_functions:
            cnt += 1
            print(f"\nLambda Function : {funcName} and Tags : {l_tags}")

            # Converting Dictionary type into List type
            ll_tags = [{'Key':key, 'Value':value} for key,value in l_tags.items()]

            # Validate if Lambda Function has all the LeanIX tags or not.
            aggregated_lix_tags = obj.validate_with_leanix_tags(leanix_tags, ll_tags)
            print(f"All User and Automated Tags are : {aggregated_lix_tags}")

            all_tags = {**aggregated_lix_tags, **user_defined_tags}

            # Converting Dictionary type into List type
            #final_tags = [{'Key':key, 'Value':value} for key,value in all_tags.items()]
            #print(f"All User and Automated Tags are : {final_tags}")

            # Final Enforcing the all the mandatory tags to resource
            obj.tagging_reconciliation_lambda(funcARN, all_tags)

if __name__ == "__main__":
    obj = ResourceDetails()
    #obj.process_resource_type("s3")
    #obj.process_resource_type("lambda")

    s3Obj = S3Processing()
    s3Obj.s3_processing("s3")

    lambdaObj = LambdaProcessing()
    lambdaObj.lambda_processing("lambda")

















