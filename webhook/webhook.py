#!/usr/bin/python3

import json
import hmac
import hashlib
import os
import logging

import boto3
from botocore.exceptions import ClientError

GITHUB_APP_WEBHOOK_SECRET = os.environ['GITHUB_APP_WEBHOOK_SECRET']
# The hmac.new function wants the key argument to be of type bytes or bytearray
hmac_key = bytes(GITHUB_APP_WEBHOOK_SECRET, 'UTF-8')

ALLOWED_REPOS = [
    "virt-s1/kite-demo",
    "virt-s1/rhel-edge",
    "coreos/coreos-installer-dracut"
]

def kite_webhook_handler(event, context):
    headers = event["headers"]
    body = json.loads(event["body"])

    if body["repository"]["full_name"] not in ALLOWED_REPOS:
        return {
            "statusCode": 400,
            "body": json.dumps("This repo is not allowed")
        }

    if headers["x-github-event"] != "workflow_job":
        return {
            "statusCode": 400,
            "body": json.dumps("workflow_job event only")
        }

    # Skipped test will not send to SQS
    # If the test is only on RHEL 8, the other tests will be skipped
    if body["workflow_job"]["conclusion"] == "skipped":
        return {
            "statusCode": 400,
            "body": json.dumps("Test skipped")
        }

    # pr-info job in each workflow only uses github action runner
    if "kite" not in body["workflow_job"]["labels"]:
        return {
            "statusCode": 400,
            "body": json.dumps(f'job {body["workflow_job"]["name"]} does not use self-hosted runner')
        }

    # Totally 3 actions, but only need queue and completed actions in this case
    if body["action"] == "in_progress":
        return {
            "statusCode": 400,
            "body": json.dumps("queued and completed actions only")
        }

    signature = headers["x-hub-signature-256"]
    if not signature or not signature.startswith("sha256="):
        return {
            "statusCode": 400,
            "body": json.dumps("X-Hub-Signature-256 required")
        }

    # Create local hash of payload
    digest = hmac.new(
        hmac_key,
        event["body"].encode(),
        hashlib.sha256
    ).hexdigest()
    print(digest)

    if not hmac.compare_digest(signature, "sha256=" + digest):
        return {
            "statusCode": 400,
            "body": json.dumps("Invalid signature")
        }

    message = {
        'headers': dict(headers),
        'payload': body
    }

    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    # Send the SQS message
    sqs_client = boto3.client('sqs')
    sqs_queue_url = sqs_client.get_queue_url(
        QueueName=os.environ['SQS_QUEUE'])['QueueUrl']

    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageBody=json.dumps(message))
    except ClientError as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': json.dumps("Send to SQS failed")
        }
    logging.info(f'Sent SQS message ID: {msg["MessageId"]}')
    return {
        'statusCode': 200,
        'body': json.dumps(f'Sent SQS message ID: {msg["MessageId"]}')
    }
