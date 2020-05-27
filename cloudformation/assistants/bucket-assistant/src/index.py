import sys
sys.path.append('./site-packages')
# flake8: noqa: E402
from crhelper import CfnResource
import boto3
from pathlib import Path


helper = CfnResource()


@helper.create
@helper.update
def on_create(event, __):
    pass


def delete_s3_objects(bucket_name):
    if bucket_name:
        s3_resource = boto3.resource("s3")
        try:
            s3_resource.Bucket(bucket_name).objects.all().delete()
            print(
                "Successfully deleted objects in bucket "
                "called '{}'.".format(bucket_name)
            )
        except s3_resource.meta.client.exceptions.NoSuchBucket:
            print(
                "Could not find bucket called '{}'. "
                "Skipping delete.".format(bucket_name)
            )
            
            
@helper.delete
def on_delete(event, __):
    s3_bucket = event["ResourceProperties"]["S3Bucket"]
    delete_s3_objects(s3_bucket)


def handler(event, context):
    helper(event, context)
