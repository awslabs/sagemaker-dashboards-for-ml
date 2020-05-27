import boto3
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from time import sleep

# import from local site-packages
# flake8: noqa: E402
sys.path.append('./site-packages')
from crhelper import CfnResource


helper = CfnResource()


@helper.create
def on_create(event, _):
    pass


@helper.update
def on_update(_, __):
    pass


def attempt_delete_acm_certificate(cert_arn):
    acm_client = boto3.client('acm')
    try:
        acm_client.delete_certificate(CertificateArn=cert_arn)
        print(
            "Successfully deleted certificate "
            "called '{}'.".format(cert_arn)
        )
        return True
    except acm_client.exceptions.ClientError as e:
        if "Could not find certificate" in str(e):
            print(
                "Could not find certificate called '{}'. "
                "Skipping delete.".format(cert_arn)
            )
            return True
        if "is in use" in str(e):
            print(
                "Could not delete certificate called '{}' "
                "because it's currently in use.".format(cert_arn)
            )
            return False
        else:
            raise e


def delete_acm_certificate(cert_arn, attempts=3, delay=30):
    deleted = attempt_delete_acm_certificate(cert_arn)
    if not deleted:
        for retry in range(attempts - 1):
            sleep(delay)
            deleted = attempt_delete_acm_certificate(cert_arn)
            if deleted:
                break
    if deleted:
        return True
    else:
        raise(Exception(
            "Could not delete certificate called '{}' "
            "after {} attempts.".format(cert_arn, attempts)
        ))


@helper.delete
def on_delete(event, __):
    cert_arn = event["ResourceProperties"]["CertificateArn"]
    delete_acm_certificate(cert_arn)


def handler(event, context):
    helper(event, context)
