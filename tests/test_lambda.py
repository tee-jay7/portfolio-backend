import sys
import os
import unittest
from unittest.mock import patch
import boto3
from moto import mock_dynamodb
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from lambda_module import lambda_handler, visit_handler 

class TestLambdaFunctions(unittest.TestCase):

    @mock_dynamodb
    @patch.dict(os.environ, {'TABLE_NAME': 'TestTable'})
    def setUp(self):
        # Set up the DynamoDB table for testing
        self.dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        self.dynamodb.create_table(
            TableName='TestTable',
            KeySchema=[
                {
                    'AttributeName': 'ID',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'ID',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        # Insert an initial item for the visit_handler test
        self.dynamodb.put_item(
            TableName='TestTable',
            Item={'ID': {'S': 'page_counter'}, 'count': {'N': '0'}}
        )

    @mock_dynamodb
    @patch.dict(os.environ, {'TABLE_NAME': 'TestTable'})
    def test_lambda_handler(self):
        # Invoke the lambda_handler function
        event = {}
        context = {}
        response = lambda_handler(event, context)

        # Parse the response body
        body = json.loads(response['body'])

        # Assert the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(body['message'], 'Hello World')
        self.assertIn('table', body)

    @mock_dynamodb
    @patch.dict(os.environ, {'TABLE_NAME': 'TestTable'})
    def test_visit_handler(self):
        # Invoke the visit_handler function
        event = {}
        context = {}
        response = visit_handler(event, context)

        # Parse the response body
        body = json.loads(response['body'])

        # Assert the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(body['message'], 'Update successful')
        self.assertEqual(body['updated_value'], '1')

        # Check the DynamoDB table to ensure the count was incremented
        result = self.dynamodb.get_item(
            TableName='TestTable',
            Key={'ID': {'S': 'page_counter'}}
        )
        self.assertEqual(result['Item']['count']['N'], '1')


if __name__ == '__main__':
    unittest.main()
