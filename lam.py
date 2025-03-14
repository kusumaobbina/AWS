import json
import boto3
from decimal import Decimal
import os

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client('s3')
table = dynamodb.Table('http-crud-tutorial-items')
tableName = 'http-crud-tutorial-items'
bucket_name = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    print(json.dumps(event))  # Log the event structure for debugging
    body = {}
    statusCode = 200
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Check if the routeKey is present in the event
        if 'routeKey' in event:
            if event['routeKey'] == "DELETE /items/{id}":
                item_id = event['pathParameters'].get('id')
                if item_id and item_id != "":
                    table.delete_item(Key={'id': item_id})
                    body = 'Deleted item ' + item_id
                else:
                    statusCode = 400
                    body = 'Missing or empty ID for DELETE request.'

            elif event['routeKey'] == "GET /items/{id}":
                item_id = event['pathParameters'].get('id')
                if item_id and item_id != "":
                    response = table.get_item(Key={'id': item_id})
                    if 'Item' in response:
                        body = response['Item']
                        body = [{'price': float(body['price']), 'id': body['id'], 'name': body['name']}]
                    else:
                        statusCode = 404
                        body = 'Item not found.'
                else:
                    statusCode = 400
                    body = 'Missing or empty ID for GET request.'

            elif event['routeKey'] == "GET /items":
                response = table.scan()
                items = response['Items']
                html_content = """
                <html>
                <head>
                    <title>Item List</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    <h1>Items List</h1>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Price</th>
                        </tr>
                """
                for item in items:
                    html_content += f"""
                    <tr>
                        <td>{item['id']}</td>
                        <td>{item['name']}</td>
                        <td>{float(item['price'])}</td>
                    </tr>
                    """
                html_content += """
                </table>
                </body>
                </html>
                """
                # Upload the HTML content to S3
                s3.put_object(
                    Bucket=bucket_name,
                    Key='index.html',
                    Body=html_content,
                    ContentType='text/html'
                )
                body = 'HTML file generated and uploaded to S3.'

            elif event['routeKey'] == "PUT /items":
                requestJSON = json.loads(event['body'])
                table.put_item(
                    Item={
                        'id': requestJSON['id'],
                        'price': Decimal(str(requestJSON['price'])),
                        'name': requestJSON['name']
                    })
                body = 'Put item ' + requestJSON['id']
        else:
            statusCode = 400
            body = 'Unsupported event format or route.'
    except KeyError:
        statusCode = 400
        body = 'Unsupported route: ' + str(event)
    except Exception as e:
        statusCode = 500
        body = str(e)

    body = json.dumps(body)
    res = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": body
    }
    return res
