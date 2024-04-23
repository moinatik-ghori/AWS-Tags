# AWS Organization Policy

## Overview

AWS Organization Policy allows organizations to centrally manage and enforce policies across multiple AWS accounts. This document provides an example of how to create an organization policy for enforcing the "CostCenter" tag requirement for EC2 instances and Lambda functions.

### Example Policy:

- **Policy Name:** RequireCostCenterTag
- **Policy Description:** This policy requires all EC2 instances and Lambda functions to have a "CostCenter" tag defined.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Require",
      "Action": "ec2:CreateTags",
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:RequestTag/CostCenter": "${aws:PrincipalTag/CostCenter}"
        }
      }
    },
    {
      "Effect": "Require",
      "Action": "lambda:TagResource",
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:RequestTag/CostCenter": "${aws:PrincipalTag/CostCenter}"
        }
      }
    }
  ]
}
```


### Pros:

- **Centralized Tag Management:** All user-defined mandatory tags can be defined at the organization level and applied across all accounts, ensuring consistency.
- **Predefined Resource Values:** Resources can be created with predefined tag values, simplifying resource management.
- **Ease of Setup:** Setting up organization policies is straightforward and can be done from the AWS Management Console or via APIs.

### Cons:

- **User Responsibility:** Users are responsible for providing the required tag while creating resources. The organization policy only validates if the tag is present, not whether it's correct.
- **Tag Deletion:** Users can delete tags after resource creation, potentially violating policy requirements.

## AWS Service Control Policy

### Overview

AWS Service Control Policy (SCP) is a feature of AWS Organizations that allows administrators to control which AWS services and resources can be accessed and managed by IAM users and roles. This document provides an example of an SCP policy to deny resource creation for EC2 instances, Lambda functions, and S3 buckets if the "CostCenter" tag is not present.

### Example Policy:

- **Policy Name:** DenyResourceCreationWithoutCostCenterTag
- **Policy Description:** This policy denies the creation of EC2 instances, Lambda functions, and S3 buckets if the "CostCenter" tag is not present.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "lambda:CreateFunction",
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "Null": {
          "aws:RequestTag/CostCenter": "true"
        }
      }
    }
  ]
}
```

## Pros:
- **Granular Resource Control:** SCPs allow administrators to specify the exact actions that are allowed or denied for each AWS service, providing fine-grained control.
- **Enforcement of Tagging Policies:** SCPs can effectively enforce tagging policies by denying resource creation if certain tags are not present.
- **Organization-wide Application:** SCPs can be applied at the organization level and automatically enforced across all member accounts.

## Cons:
- **Character Limit:** SCPs have a character limit for policy definitions, which may restrict the complexity of policies that can be defined.
- **Limited Error Description:** When a resource creation is denied by an SCP, the error message provided to the user may not be descriptive enough to understand why the action was denied, leading to confusion.



