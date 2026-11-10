import os
import boto3

TABLE_NAME = os.environ['TABLE_NAME']
MAX_MONITORS = int(os.environ.get('MAX_MONITORS', '20'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
