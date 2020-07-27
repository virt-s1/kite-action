#!/usr/bin/python3

import os
import time
import subprocess

from bottle import route, run
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


@route("/runner/<names>", method="PUT")
def shut_runner(names):
    token = os.environ.get("GITHUB_ACCESS_TOKEN")
    api = "https://api.github.com/orgs/virt-s1/actions/"
    headers = {
        "User-Agent": "kite-action",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token " + token
    }
    (runner_name, pod_name) = names.split(",")

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
    requests.delete(api + "runners/" + str(runner_id), headers=headers)
    # delete pod
    # get token in container first
    with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as token_file:
        sa_token = token_file.read()

    subprocess.call(["oc", "login", "https://paas.psi.redhat.com:443", "--token=" + sa_token])
    subprocess.call(["oc", "project", "virt-qe-3rd"])
    subprocess.call(["oc", "delete", "--grace-period=0", "--force", "pods/" + pod_name])


# used by readinessProbe and livenessProbe on openshift
@route("/probe", method="GET")
def oc_probe():
    return("Controller is running")


# dev
# run(reloader=True, debug=True)
# prod
run(server="bjoern")
