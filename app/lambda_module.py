import json
import boto3
import os
import datetime

datetime_now = datetime.datetime.now(datetime.UTC)


client = boto3.client('dynamodb', region_name='eu-west-1') 


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def lambda_handler(event, context):
    response = client.describe_table(
        TableName=os.getenv('TABLE_NAME')
    )
    return {
        "statusCode": 200,
        "headers": {
             "Access-Control-Allow-Origin": '*',
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Hello World",
            'table': response
        }, cls=DateTimeEncoder)
    }


def visit_handler(event, context):
    table_name = os.getenv('TABLE_NAME')
    key_value = "page_counter"

    response = client.update_item(
        TableName=table_name,
        Key={
            'ID': {'S': key_value}
        },
        UpdateExpression="SET #attrName = if_not_exists(#attrName, :start) + :inc",
        ExpressionAttributeNames={
            "#attrName": "count" 
        },
        ExpressionAttributeValues={
            ":start": {"N": "0"},
            ":inc": {"N": "1"}
        },
        ReturnValues="UPDATED_NEW"
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*',
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Update successful",
            "updated_value": response['Attributes']['count']['N']
        })
    }

