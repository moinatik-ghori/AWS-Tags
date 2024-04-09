# AWS Tagging Enforcement and Reconciliation

The AWS Tagging Enforcement Program is designed to streamline the management of AWS resources by enforcing tagging standards across S3 buckets and Lambda functions. Tags provide metadata to resources, allowing for easy identification, organization, and management. This program ensures that resources are tagged appropriately, following both user-defined conventions and automated tagging provided by LeanIX.

## Purpose

1. **Consistency**: Ensures uniformity in tagging practices across all resources, facilitating easier tracking and management.
2. **Compliance**: Enforces compliance with tagging standards set by the organization, ensuring that resources are properly labeled for accountability and cost allocation.
3. **Automation**: Integrates with LeanIX automation to automatically apply tags based on predefined rules, reducing manual effort and potential errors.
4. **Reporting**: Generates reports on compliant resources, providing visibility into adherence to tagging standards and aiding in auditing processes.

## Key Features

1. **Tag Aggregation**: Aggregates user-defined tags and LeanIX automation-provided tags to create comprehensive tagging profiles for resources.
2. **Tagging Reconciliation**: Validates existing tags against LeanIX tags and applies missing tags to ensure completeness.
3. **Reporting**: Generates reports detailing compliant resources, facilitating monitoring and compliance tracking.
4. **Scalability**: Scalable to manage a large number of resources efficiently, ensuring consistent enforcement across the AWS environment.

## How it Works

The program consists of two main modules:

1. **S3 Processing**: Handles tagging enforcement for S3 buckets.
2. **Lambda Processing**: Manages tagging enforcement for Lambda functions.

Both modules follow a similar workflow:

1. **Retrieve Tags**: Fetches existing tags associated with resources.
2. **Load User-defined Tags**: Loads user-defined tagging conventions from a JSON file.
3. **Call LeanIX**: Contacts LeanIX to retrieve automated tags based on predefined rules.
4. **Tag Validation**: Validates existing tags against LeanIX tags and aggregates them to create comprehensive tagging profiles.
5. **Tag Enforcement**: Applies missing tags to resources to ensure compliance with tagging standards.
6. **Reporting**: Generates reports on compliant resources, providing visibility into adherence to tagging standards.

## Dependencies

- `boto3` - AWS SDK for Python
- `requests` - HTTP library

## Classes and Functions

### `S3Processing`

- **Description**: Handles processing related to S3 buckets.
- **Methods**:
  - `s3_processing(res_type)`: Main function for S3 processing.
  - `get_s3_functions_with_tags()`: Retrieves S3 buckets with their associated tags.
  - `call_leanix(res_type, acct_id)`: Calls LeanIX API to retrieve tags.
  - `load_user_tags()`: Loads user-defined tags from a JSON file.
  - `validate_with_leanix_tags(leanIX_tags, resource_tags)`: Validates and aggregates LeanIX tags with existing tags.
  - `tagging_reconciliation_s3(res_id, final_tags)`: Enforces tags on S3 buckets.
  - `get_user_defined_tags(res_type, acct_id)`: Retrieves user-defined tags.
  - `generate_report(res_type, bucket)`: Generates a report for compliant resources.
  

### `LambdaProcessing`

- **Description**: Handles processing related to Lambda functions.
- **Methods**:
  - `lambda_processing(res_type)`: Main function for Lambda processing.
  - `get_lambda_functions_with_tags()`: Retrieves Lambda functions with their associated tags.
  - `call_leanix(res_type, acct_id)`: Calls LeanIX API to retrieve tags.
  - `load_user_tags()`: Loads user-defined tags from a JSON file.
  - `validate_with_leanix_tags(leanIX_tags, resource_tags)`: Validates and aggregates LeanIX tags with existing tags.
  - `tagging_reconciliation_lambda(res_id, final_tags)`: Enforces tags on Lambda functions.
  - `get_user_defined_tags(res_type, acct_id)`: Retrieves user-defined tags.
  - `generate_report(res_type, funcName)`: Generates a report for compliant resources.
  

## Usage

To use this program, execute the main section of the script which processes both S3 buckets and Lambda functions.

```python
if __name__ == "__main__":
    s3Obj = S3Processing()
    s3Obj.s3_processing("s3")

    lambdaObj = LambdaProcessing()
    lambdaObj.lambda_processing("lambda")
