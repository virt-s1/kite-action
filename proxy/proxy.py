#!/usr/bin/python3

import json
import os
import time
import subprocess
import boto3

SQS_QUEUE = os.environ["SQS_QUEUE"]
SQS_REGION = os.environ["SQS_REGION"]

sqs = boto3.resource("sqs", region_name=SQS_REGION)
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE)

print("Fetching message from queue")

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
            cmd = ["ansible-playbook"]

            labels = payload["workflow_job"]["labels"]
            # set cloud_profile
            if "rhos-01" in labels:
                cmd += ["-e", "cloud_profile=rhos-01"]

            # set os
            suported_os = [
                "centos-stream-8",
                "centos-stream-9",
                "rhel-8-6",
                "rhel-8-7",
                "rhel-9-0",
                "rhel-9-1"
            ]
            for i in suported_os:
                if i in labels:
                    cmd += ["-e", "os="+i]

            # set openstack flavor
            if "large" in labels:
                cmd += ["-e", "flavor_type=large"]

            # set arch
            if "x86_64" in labels:
                cmd += ["-e", "arch=x64"]

            # set repo_fullname
            cmd += ["-e", "repo_fullname="+payload["repository"]["full_name"]]

            # set runner labels
            label_str = ",".join(labels)
            cmd += ["-e", "runner_labels="+label_str]

            # final ansible playbook
            cmd += ["install_runner.yaml"]

            # run ansible playbook
            subprocess.Popen(cmd)
            print(f"Github runner - {label_str} deploy starting")

        # Remove runner instance for completed action
        if payload["action"] == "completed":
            cmd = ["ansible-playbook"]

            labels = payload["workflow_job"]["labels"]
            # set cloud_profile
            if "rhos-01" in labels:
                cmd += ["-e", "cloud_profile=rhos-01"]

            # set instance name
            runner_name = payload["workflow_job"]["runner_name"]
            if runner_name:
                cmd += ["-e", "instance_name="+runner_name]

                # final ansible playbook
                cmd += ["delete_os_instance.yaml"]

                # run ansible playbook to delete instance
                subprocess.Popen(cmd)
                print(f"Github runner - {runner_name} destroy starting")

        # Delete the message if we made it this far.
        message.delete()
        print(f"Message with ID: {message.message_id} deleted")

    time.sleep(5)
