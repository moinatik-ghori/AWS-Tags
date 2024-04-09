import boto3
import json
import requests
from botocore.exceptions import ClientError
import logging
import os


class LambdaProcessing():
    def __init__(self):
        self.user_tags = {}

    def get_lambda_functions_with_tags(self):
        print(f"\nCalling Function:get_lambda_functions_with_tags ")
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


    def tagging_reconciliation_lambda(self, res_id, final_tags):
        print(f"\nCalling Function:tagging_reconciliation_lambda ")
        try:
            client = boto3.client('lambda')
            client.tag_resource(Resource=res_id, Tags=final_tags)
            print(f"Tagging Enforcement for Lambda {res_id} has been completed. ")
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

    def generate_report(self, res_type, funcName):
        print(f"\nCalling Function: generate_report")
        try:
            filePath = "Reports/Complient_Resources_Report.json"

            if os.path.exists(filePath):
                with open("Reports/Complient_Resources_Report.json", "r") as file:
                    report = json.load(file)
            else:
                report = {}

            if res_type in report:
                report[res_type][funcName] = "Complient"
            else:
                report[res_type] = {funcName: "Complient"}

            json_str = json.dumps(report, indent=4)

            with open("Reports/Complient_Resources_Report.json", "w") as file:
                file.write(json_str)
            print(f"Report has been generated.")
            file.close()
        except Exception as e:
            print(f"Error Message : {e}")

    def lambda_processing(self,res_type):
        try:
            self.display_dash(100)
            print(f"Lambda Processing")
            self.display_dash(100)

            # Getting User Defined Tags
            user_defined_tags = self.get_user_defined_tags(res_type, "B1")
            print(f"User defined Tags for Lambda Functions are : {user_defined_tags}")

            # Getting LeanIX Automation-Tags
            leanix_tags = self.call_leanix(res_type, "B1")
            print(f"LeanIX Automation Provided Tags: {leanix_tags}")

            # Get Lambda functions and tags associated with it
            cnt = 0
            l_functions = self.get_lambda_functions_with_tags()
            for funcName, funcARN, l_tags in l_functions:
                print(f"Lambda Function : {funcName} and Tags : {l_tags}")

                # Converting Dictionary type into List type
                ll_tags = [{'Key':key, 'Value':value} for key,value in l_tags.items()]

                # Validate if Lambda Function has all the LeanIX tags or not.
                aggregated_lix_tags = self.validate_with_leanix_tags(leanix_tags, ll_tags)
                print(f"All User and Automated Tags are : {aggregated_lix_tags}")

                all_tags = {**aggregated_lix_tags, **user_defined_tags}

                # Final Enforcing the all the mandatory tags to resource
                self.tagging_reconciliation_lambda(funcARN, all_tags)
                cnt += 1
                self.generate_report(res_type, funcName)
                self.display_dash(100)

            print(f"\nNumber of Lambda Function Processed : {cnt}\n")
        except Exception as e:
            print(f"Error Message : {e}")




















