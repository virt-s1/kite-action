#!/usr/bin/python3

import json
import hmac
import hashlib
import os
from base64 import b64decode
import time
import http.client
from http import HTTPStatus
import urllib.parse
import errno
import socket

import boto3

ENCRYPTED_GITHUB_APP_WEBHOOK_SECRET = os.environ['GITHUB_APP_WEBHOOK_SECRET']
# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
GITHUB_APP_WEBHOOK_SECRET = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(ENCRYPTED_GITHUB_APP_WEBHOOK_SECRET),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext']

# Github access token
ENCRYPTED_GITHUB_ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']
GITHUB_ACCESS_TOKEN = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(ENCRYPTED_GITHUB_ACCESS_TOKEN),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')


def request(url, method, data="", headers=None):
    if headers is None:
        headers = {}
    headers["User-Agent"] = "kite-action"
    headers["Authorization"] = "token " + GITHUB_ACCESS_TOKEN
    url_obj = urllib.parse.urlparse(url)

    connected = False
    bad_gateway_errors = 0
    while not connected and bad_gateway_errors < 5:
        if url_obj.scheme == 'http':
            conn = http.client.HTTPConnection(url_obj.netloc)
        else:
            conn = http.client.HTTPSConnection(url_obj.netloc)
        connected = True

        try:
            conn.request(method, url_obj.path, data, headers)
            response = conn.getresponse()
            if response.status == HTTPStatus.BAD_GATEWAY:
                bad_gateway_errors += 1
                conn = None
                connected = False
                time.sleep(bad_gateway_errors * 2)
                continue
            break
        # This happens when GitHub disconnects in python3
        except ConnectionResetError:
            if connected:
                raise
            conn = None
        # This happens when GitHub disconnects a keep-alive connection
        except http.client.BadStatusLine:
            if connected:
                raise
            conn = None
        # This happens when TLS is the source of a disconnection
        except socket.error as ex:
            if connected or ex.errno != errno.EPIPE:
                raise
            conn = None
    heads = {}
    for (header, value) in response.getheaders():
        heads[header.lower()] = value

    return {
        "status": response.status,
        "reason": response.reason,
        "headers": heads,
        "data": response.read().decode('utf-8')
    }


def kite_webhook_handler(event, context):
    headers = event["headers"]
    body = json.loads(event["body"])

    if headers["x-github-event"] != "check_run":
        return {
            "statusCode": 400,
            "body": json.dumps("check_run event only")
        }

    if body["action"] != "created":
        return {
            "statusCode": 400,
            "body": json.dumps("created action only")
        }

    signature = headers["x-hub-signature"]
    if not signature or not signature.startswith("sha1="):
        return {
            "statusCode": 400,
            "body": json.dumps("X-Hub-Signature required")
        }

    # Create local hash of payload
    digest = hmac.new(
        GITHUB_APP_WEBHOOK_SECRET,
        event["body"].encode(),
        hashlib.sha1
    ).hexdigest()
    print(digest)

    if not hmac.compare_digest(signature, "sha1=" + digest):
        return {
            "statusCode": 400,
            "body": json.dumps("Invalid signature")
        }

    response = request("https://api.github.com/orgs/virt-s1/members", "GET")
    allowed_users = [x["login"] for x in json.loads(response["data"])]
    print(allowed_users)
    pr_sender = body["sender"]["login"]
    if pr_sender not in allowed_users:
        return {
            "statusCode": 400,
            "body": json.dumps("PR sender is not members of virt-s1 org")
        }

    message = {
        'headers': dict(headers),
        'payload': body
    }
    sqs = boto3.resource('sqs', region_name=os.environ['SQS_REGION'])
    queue = sqs.get_queue_by_name(QueueName=os.environ['SQS_QUEUE'])
    sqs_response = queue.send_message(
        MessageBody=json.dumps(message)
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f"SQS Message ID: {sqs_response.get('MessageId')}")
    }
