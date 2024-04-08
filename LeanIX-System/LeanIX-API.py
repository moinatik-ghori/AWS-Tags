from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("mandatory_tags")

mandatory_tags = {
    "s3" : {
        "A1" : {
            "system-name"            : "IX-system-name_A1",
            "system-lifecycle"       : "IX-system-lifecycle_A1",
            "system-support_ag_name" : "IX-system-support_ag_name_A1",
            "system-support_ag_id"   : "IX-system-support_ag_id_A1",
            "system-change_ag_name"  : "IX-system-change_ag_name_A1",
            "system-change_ag_id"    : "IX-system-change_ag_id_A1"
        },
        "A2" : {
            "system-name"            : "IX-system-name_A2",
            "system-lifecycle"       : "IX-system-lifecycle_A2",
            "system-support_ag_name" : "IX-system-support_ag_name_A2",
            "system-support_ag_id"   : "IX-system-support_ag_id_A2",
            "system-change_ag_name"  : "IX-system-change_ag_name_A2",
            "system-change_ag_id"    : "IX-system-change_ag_id_A2"
        }
    },
    "ec2" : {
        "B1" : {
            "system-name"            : "IX-system-name_B1",
            "system-lifecycle"       : "IX-system-lifecycle_B1",
            "system-support_ag_name" : "IX-system-support_ag_name_B1",
            "system-support_ag_id"   : "IX-system-support_ag_id_B1",
            "system-change_ag_name"  : "IX-system-change_ag_name_B1",
            "system-change_ag_id"    : "IX-system-change_ag_id_B1"
        },
        "B2" : {
            "system-name"            : "IX-system-name_B2",
            "system-lifecycle"       : "IX-system-lifecycle_B2",
            "system-support_ag_name" : "IX-system-support_ag_name_B2",
            "system-support_ag_id"   : "IX-system-support_ag_id_B2",
            "system-change_ag_name"  : "IX-system-change_ag_name_B2",
            "system-change_ag_id"    : "IX-system-change_ag_id_B2"
        }
    }
}

@app.route('/tags', methods=['GET'])
def get_tags():
    print(f"I am in Get_Tags Method")
    resource_type = request.args.get('resource_type')
    account_id = request.args.get('account_id')

    if (resource_type in mandatory_tags) and (account_id in mandatory_tags[resource_type]):
        return jsonify(mandatory_tags[resource_type][account_id])
    else:
        return jsonify("Error: Combination of Resource ID and Account ID not found"), 404


if __name__ == "__main__":
    app.run(debug=True)