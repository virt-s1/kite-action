#!/usr/bin/python3

import os
import time
import subprocess
import yaml
import random
import string

from bottle import route, run
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


@route("/runner/delete/<name>", method="PUT")
def shut_runner(name):
    token = os.environ.get("GITHUB_ACCESS_TOKEN")
    api = "https://api.github.com/orgs/virt-s1/actions/"
    headers = {
        "User-Agent": "kite-action",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token " + token
    }
    # runner_name: github action runner name (Github->Actions)
    # pod_name: openshift pod name (openshift->pod->name)
    runner_name = pod_name = name

    # Wordaround issue - Max retries exceeded with URL in requests
    # From: https://stackoverflow.com/questions/23013220
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.keep_alive = False

    # 3 minutes timeout (18*10 seconds)
    # wait until action runner is not busy to remove runner and delete pod
    retry_times = 18
    while (retry_times > 0):
        result = session.get(api + "runners", headers=headers).json()
        for x in result["runners"]:
            if (x["name"] == runner_name):
                this_runner = x
        if not this_runner["busy"]:
            runner_id = this_runner["id"]
            break
        time.sleep(10)
        retry_times -= 1

    # remove action runner from org
    session.delete(api + "runners/" + str(runner_id), headers=headers)
    # delete pod
    subprocess.call(["oc", "delete", "--grace-period=0", "--force", "pods/" + pod_name])


@route("/runner/create/<repo>", method="PUT")
def create_runner(repo):
    # random string for pod name
    letters_and_digits = string.ascii_lowercase + string.digits
    surfix = ''.join((random.choice(letters_and_digits) for i in range(5)))
    # pod object
    pod_obj = {
        'kind': 'Pod',
        'apiVersion': 'v1',
        'metadata': {
            'name': repo + "-runner-" + surfix
        },
        'spec': {
            'containers': [
                {
                    'name': 'forever-github-runner',
                    'image': 'docker-registry.default.svc:5000/virt-qe-3rd/github-runner:latest',
                    'imagePullPolicy': 'IfNotPresent',
                    'resources': {
                        'requests': {
                            'memory': '500Mi',
                            'cpu': '500m'
                        },
                        'limits': {
                            'memory': '2Gi',
                            'cpu': '1000m'
                        }
                    },
                    'env': [
                        {
                            'name': 'KITE_CONTROLLER_API_NETLOC',
                            'value': 'https://kite-controller-virt-qe-3rd.cloud.paas.psi.redhat.com'
                        },
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
                        },
                        {
                            'name': 'RUNNER_POD_NAME',
                            'valueFrom': {
                                'fieldRef': {
                                    'fieldPath': 'metadata.name'
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
    subprocess.call(["oc", "create", "-f", "runner-pod.yaml"])


# used by readinessProbe and livenessProbe on openshift
@route("/probe", method="GET")
def oc_probe():
    return("Controller is running")


# dev
# run(reloader=True, debug=True)
# prod
run(host="0.0.0.0", port=8080, server="bjoern")
