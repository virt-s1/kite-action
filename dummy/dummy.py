#!/usr/bin/python3

import os
import json
import time
import subprocess
import yaml
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# make date(month+day) as pod name surfix
surfix = date.today().strftime("%m%d")
runner_name = "dummy-runner-" + surfix
# pod object
pod_obj = {
    'kind': 'Pod',
    'apiVersion': 'v1',
    'metadata': {
        'name': runner_name
    },
    'spec': {
        'containers': [
            {
                'name': runner_name,
                'image': 'docker-registry.default.svc:5000/virt-qe-3rd/github-runner:latest',
                'imagePullPolicy': 'IfNotPresent',
                'resources': {
                    'requests': {
                        'memory': '250Mi',
                        'cpu': '100m'
                    },
                    'limits': {
                        'memory': '500Mi',
                        'cpu': '500m'
                    }
                },
                'env': [
                    {
                        'name': 'RUNNER_ORGANIZATION_URL',
                        'value': 'https://github.com/virt-s1'
                    },
                    {
                        'name': 'RUNNER_LABELS',
                        'value': 'kite-runner'
                    },
                    {
                        'name': 'GITHUB_ACCESS_TOKEN',
                        'valueFrom': {
                            'secretKeyRef': {
                                'name': 'github-access-token',
                                'key': 'token'
                            }
                        }
                    }
                ]
            }
        ]
    }
}
# save pod object to yaml file
with open("runner-pod.yaml", "w") as f:
    yaml.dump(pod_obj, f)
# create pod
subprocess.run(["oc", "create", "-f", "runner-pod.yaml"])

# wait 360*10 seonds until pod's running
retry_times = 360
while (retry_times > 0):
    raw_output = subprocess.run(
        ["oc", "get", "pod", runner_name, "-o", "json"], stdout=subprocess.PIPE)
    output = json.loads(raw_output.stdout)
    print(f'current status: {output["status"]["phase"]}')

    if output["status"]["phase"] == "Running":
        break

    time.sleep(10)
    retry_times -= 1

# wait for new runner running
token = os.environ.get("GITHUB_ACCESS_TOKEN")
api = "https://api.github.com/orgs/virt-s1/actions/"
headers = {
    "User-Agent": "kite-action",
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "token " + token
}

# Wordaround issue - Max retries exceeded with URL in requests
# From: https://stackoverflow.com/questions/23013220
session = requests.Session()
retry = Retry(connect=5, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.keep_alive = False

# 10 minutes timeout (60*10 seconds)
# wait until action runner is not busy to remove runner and delete pod
retry_times = 60
while (retry_times > 0):
    result = session.get(api + "runners", headers=headers).json()
    for x in result["runners"]:
        if x["name"] == runner_name and x["status"] == "online":
            print(f"{runner_name} is online")
            break
    else:
        time.sleep(10)
        retry_times -= 1
        continue
    break

# delete pod
subprocess.run(["oc", "delete", "--grace-period=0", "--force", "pods/" + runner_name])

# un-register old dummy runner because we have a new one already
# do not wait for Github audo-delete every 30 days
for x in result["runners"]:
    if x["name"].startswith("dummy-runner") and x["name"] != runner_name:
        runner_id = x["id"]
        # un-register old dummy runner from org
        session.delete(api + "runners/" + str(runner_id), headers=headers)
        print(f"delete old dummy runner {x['name']}")
