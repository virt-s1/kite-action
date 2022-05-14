#!/usr/bin/python3

import json
import os
import time

import boto3
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

SQS_QUEUE = os.environ["SQS_QUEUE"]
SQS_REGION = os.environ["SQS_REGION"]
CONTROLLER_API_NETLOC = os.environ["CONTROLLER_API_NETLOC"]

sqs = boto3.resource("sqs", region_name=SQS_REGION)
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE)

print("Fetching message from queue")

# Wordaround issue - Max retries exceeded with URL in requests
# From: https://stackoverflow.com/questions/23013220
session = requests.Session()
retry = Retry(connect=5, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.keep_alive = False
# Do not need verify certificate because it's internal
session.verify = False

# All messages in SQS are allowed and valid
# Do not check/verify message again
# Do not check x-github-event here because it's filtered by webhook already
while True:
    for message in queue.receive_messages(
            WaitTimeSeconds=20, MaxNumberOfMessages=10):
        print(f"Got message: {message.message_id}")
        parsed = json.loads(message.body)
        payload = parsed["payload"]

        # Create runner for queued action
        if payload["action"] == "queued":
            labels = payload["workflow_job"]["labels"]
            label_str = ",".join(labels)
            # Call API to create runner
            session.put(CONTROLLER_API_NETLOC + "/runner/create/" + label_str)
            print(f"Github runner - {label_str} deploy starting")

        # Remove runner instance for completed action
        if payload["action"] == "completed":
            runner_name = payload["workflow_job"]["runner_name"]
            # Call API to delete runner instance
            session.put(CONTROLLER_API_NETLOC + "/runner/delete/" + runner_name)
            print(f"Github runner - {runner_name} destroy starting")

        # Delete the message if we made it this far.
        message.delete()
        print(f"Message with ID: {message.message_id} deleted")

    time.sleep(5)
