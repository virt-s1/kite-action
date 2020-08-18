#!/usr/bin/python3

import os
import json
import time
import subprocess
import yaml
from datetime import datetime


import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# list all pods running for more than 5 minutes
raw_output = subprocess.run(
    ["oc", "get", "pod", "-l", "kite=self-hosted-runner", "-o", "json"],
    stdout=subprocess.PIPE)
output = json.loads(raw_output.stdout)

if output["items"]:
    containers = [x["status"]["containerStatuses"][0] for x in output["items"]]

    # Python's datetime does not support the military timezone suffixes like 'Z' suffix for UTC.
    # filter function
    def filter_removing(x):
        allowed_delta = 300
        delta = datetime.utcnow() - datetime.strptime(
            x["state"]["running"]["startedAt"], '%Y-%m-%dT%H:%M:%SZ')
        if delta.total_seconds() >= allowed_delta:
            return True
        else:
            return False

    # containers in running status and started for more than 5 minutes
    removing_pods = list(filter(filter_removing, containers))
    print(removing_pods)

    # list all online and not busy runners
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

    result = session.get(api + "runners", headers=headers).json()
    print(result)
    if result["runners"]:
        runners = [x for x in result["runners"] if x["status"] == "online" and not x["busy"]]
        runners_obj = {}
        for x in runners:
            runners_obj[x["name"]] = x["id"]
        print(runners_obj)

        delete_pods = []
        removed_runners = []
        for runner in removing_pods:
            if runner["name"] in runners_obj.keys():
                # remove action runner from org
                session.delete(api + "runners/" + str(runners_obj[runner["name"]]), headers=headers)
                # delete pod
                subprocess.call(
                    ["oc", "delete", "--grace-period=0", "--force", "pods/" + runner["name"]])
                removed_runners.append(runner["name"])
            else:
                delete_pods.append(runner["name"])

        # delete pod if pod is not registed as runner
        if delete_pods:
            print(delete_pods)
            for pod in delete_pods:
                subprocess.call(["oc", "delete", "--grace-period=0", "--force", "pods/" + pod])
    else:  # pods not registered as runner
        for runner in removing_pods:
            subprocess.call(
                ["oc", "delete", "--grace-period=0", "--force", "pods/" + runner["name"]])
else:
    print("Github runner pod not found")
