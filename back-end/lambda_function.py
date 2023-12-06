import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    filename = event['filename']

    print(event)
    print(type(event))
    print(filename)

    # Print or log the filename
    logger.info(f"Received filename: {filename}")

    # Return a simple response
    response_message = f"Filename {filename} received successfully"
    return {
        'statusCode': 200,
        'body': {'message': response_message},
    }
