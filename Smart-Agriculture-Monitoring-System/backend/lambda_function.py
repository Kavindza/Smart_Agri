import json
import logging
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("SensorData")


def lambda_handler(event, context):
    """
    AWS Lambda function to receive simulated IoT sensor data,
    store it in DynamoDB, and generate a mock alert if moisture is low.
    """

    try:
        # Parse incoming JSON
        if "body" in event:
            data = json.loads(event["body"])
        else:
            data = event

        # Extract sensor values
        device_id = data["device_id"]
        temperature = float(data["temperature"])
        moisture = float(data["moisture"])
        ph = float(data["pH"])

        timestamp = datetime.utcnow().isoformat()

        # Log incoming data
        logger.info(f"Received Sensor Data: {data}")

        # Store in DynamoDB
        table.put_item(
            Item={
                "device_id": device_id,
                "timestamp": timestamp,
                "temperature": temperature,
                "moisture": moisture,
                "pH": ph
            }
        )

        logger.info("Sensor data stored successfully.")

        # Mock alert
        alert = None
        if moisture < 30:
            alert = {
                "type": "Low Moisture",
                "message": f"Warning! Soil moisture is {moisture}%. Irrigation recommended.",
                "device_id": device_id,
                "timestamp": timestamp
            }

            logger.warning(f"ALERT: {alert}")

            # Future enhancement:
            # Publish alert to Amazon SNS, EventBridge, or AWS IoT Core

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Sensor data processed successfully.",
                "stored": True,
                "alert": alert
            })
        }

    except KeyError as e:
        logger.error(f"Missing field: {str(e)}")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": f"Missing required field: {str(e)}"
            })
        }

    except ClientError as e:
        logger.error(e.response["Error"]["Message"])

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "DynamoDB error occurred."
            })
        }

    except Exception as e:
        logger.exception("Unexpected error")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }