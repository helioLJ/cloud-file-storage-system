import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    filename = body.get('filename')

    # Print or log the filename
    logger.info(f"Received filename: {filename}")

    # Log other information about the processing
    logger.info("Lambda function executed successfully.")

    # Return a simple response
    response_message = f"Filename {filename} received successfully"
    return {
        'statusCode': 200,
        'body': json.dumps({'message': response_message}),
    }
