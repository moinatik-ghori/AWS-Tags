class LeanIX():
    def __init__(self):
        print(f"LeanIX System Processing")

    def call_leanix(self):
        print(f"Calling LeanIX")

        # Getting LeanIX Automation-Tags
        leanix_tags = self.call_leanix("s3", bucket, "A1")
        print(f"LeanIX Automation Provided Tags: {leanix_tags}")

        all_tags = {**aggregated_s3ix_tags, **user_defined_tags}

        # Converting Dictionary type into List type
        final_tags = [{'Key': key, 'Value': value} for key, value in all_tags.items()]
        print(f"Final All Mandatory Tags and User Defined Tags : {final_tags}")

    def get_user_provided_tags(self):
        print(f"Getting User provided tags")

        # Getting User Defined Tags
        user_defined_tags = self.get_user_defined_tags("s3", bucket, "A1")
        print(f"User Tags for bucket {bucket} are : {user_defined_tags}")

    def validate_tags(self):
        print(f"Validating the existing tags, user defined tags and automation tags")

        # Validate if S3 Bucket has all the LeanIX tags or not.
        aggregated_s3ix_tags = self.validate_with_mandatory_tags(leanix_tags, s3_tags)
        print(f"All Mandatory Tags are : {aggregated_s3ix_tags}")


