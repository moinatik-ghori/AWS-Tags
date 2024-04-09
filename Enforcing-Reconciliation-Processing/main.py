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


if __name__ == "__main__":
    # S3 Bucket Processing
    s3Obj = S3Processing()
    s3Obj.s3_processing("s3")

    # Lambda Function Processing
    lambdaObj = LambdaProcessing()
    lambdaObj.lambda_processing("lambda")

















