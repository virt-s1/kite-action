#!/usr/bin/python3

import json
import os
import time

import boto3
import requests

SQS_QUEUE = os.environ["SQS_QUEUE"]
SQS_REGION = os.environ["SQS_REGION"]
CONTROLLER_API_NETLOC = os.environ["CONTROLLER_API_NETLOC"]

sqs = boto3.resource("sqs", region_name=SQS_REGION)
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE)

print("Fetching message from queue")

while True:
    for message in queue.receive_messages(
            WaitTimeSeconds=20, MaxNumberOfMessages=10):
        print(f"Got message: {message.message_id}")
        parsed = json.loads(message.body)
        headers = parsed["headers"]
        payload = parsed["payload"]

        # Check message
        if headers["x-github-event"] == "check_run" and payload["action"] == "created":
            # Get repo name
            repo_name = payload["repository"]["name"]

            # Call API to create runner pod
            requests.put(CONTROLLER_API_NETLOC + "/runner/create/" + repo_name)
            print(f"Github runner - {repo_name} deploy starting")

        # Delete the message if we made it this far.
        message.delete()
        print(f"Message with ID: {message.message_id} deleted")

    time.sleep(5)
