class TagReconciliation():
    def __init__(self):
        print(f"Tag Reconciliation Processing")

    def tag_reconcilieation(self,res_type,res_id,final_tags):
        # Final Enforcing the all the mandatory tags to resource
        print(f"Function: tag_reconcilieation : {res_id}")
        if res_type == "s3":
            self.tagging_reconciliation_s3(res_id, final_tags)