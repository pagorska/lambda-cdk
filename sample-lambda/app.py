import requests
import json
#import boto3

def lambda_handler(event, context):
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        response.raise_for_status()
        data = response.json()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'api_response': data['body'],
                'message': 'Data fetched successfully\n'
            }),
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error fetching data: {str(e)}'
        }