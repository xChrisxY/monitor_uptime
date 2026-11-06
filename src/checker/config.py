import os 
import boto3

TABLE_NAME = os.environ['TABLE_NAME']
TOPIC_ARN = os.environ['TOPIC_ARN']
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT_SECONDS', '5'))
FAILURE_THRESHOLD = int(os.environ.get('FAILURE_THRESHOLD', '2'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
sns = boto3.client('sns')