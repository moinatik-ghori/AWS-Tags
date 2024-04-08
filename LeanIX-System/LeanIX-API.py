from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("mandatory_tags")

mandatory_tags = {
    "S3" : {
        "A1" : {
            "tag1" : "val1",
            "tag2" : "val2",
            "tag3" : "val3"
        },
        "A2" : {
            "tag4" : "val4",
            "tag5" : "val5",
            "tag6" : "val6"
        }
    },
    "EC2" : {
        "B1" : {
            "tag7" : "val7",
            "tag8" : "val8",
            "tag9" : "val9"
        },
        "B1" : {
            "tag10" : "val10",
            "tag11" : "val11",
            "tag12" : "val12"
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