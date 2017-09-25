#!/usr/bin/env python

import json
import subprocess
import sys
import time


def wait_for_proxy():
    stdout = sys.stdout
    sys.stdout = sys.stderr
    input("UI proxy expired. Please create a new proxy (see README) and press ENTER to continue.")
    sys.stdout = stdout


STATUS_ATTEMPTS = 20

jobid = sys.argv[1]

# try to get status 10 times
for i in range(STATUS_ATTEMPTS):
    try:
        res = subprocess.run("PATH=${{PATH#*:}} glite-wms-job-status --json {}".format(jobid), check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        res = json.loads(res.stdout.decode())
    except subprocess.CalledProcessError as e:
        if "UI_PROXY_EXPIRED" in e.stdout.decode():
            wait_for_proxy()
            continue
        if i >= STATUS_ATTEMPTS - 1:
            if "already purged" in e.stdout.decode():
                print("purged")
                exit(0)
            print("glite-wms-job-status error: ", e.stdout, file=sys.stderr)
            raise e
        else:
            time.sleep(5)

status = res[jobid]["Current Status"]
if status == "Done(Success)":
    print("success")
elif status == "Done(Exit Code !=0)":
    print("failed")
elif status.startswith("Done"):
    print("failed")
elif status == "Cancelled":
    print("failed")
elif status == "Aborted":
    print("failed")
elif status == "Cleared":
    print("failed")
else:
    print("running")