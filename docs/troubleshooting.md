# Troubleshooting Guide

## 'CREATE_FAILED', 'ROLLBACK_IN_PROGRESS' or 'ROLLBACK_COMPLETE'

Your AWS CloudFormation Stack could have failed for a few different
reasons. One example could be that your AWS user account doesn't have the
necessary permissions to create all of the resources included in the AWS
CloudFormation Stack. You can debug the issue as follows:

* Click on the failed stack (that has status
  'CREATE_FAILED','ROLLBACK_IN_PROGRESS' or 'ROLLBACK_COMPLETE')
* Click on the 'Events' tab
* Scroll though the events and look for resources with 'Status' of
  'CREATE_FAILED'
* Check the 'Status reason'

When an error occurs within a nested stack the error message might be
vague. You can debug issues within nested stack as follows:

* Click on the 'Resources' tab of the original failed stack.
* Click on the 'Physical ID' link for the failed nested stack.
* Check the 'Events' tab for the nested stack (same as for original stack).

## 'No email provided but desired delivery medium was Email'

`AddCognitoAuthentication` is set to `true` by default on the AWS
CloudFormation template to ensure the dashboard is secured out of the box.
You are likely to see this error if you kept this default but didn't
provide an email address to send the temporary credentials to. You should
set the `CognitoAuthenticationSampleUserEmail` parameter on the AWS
CloudFormation template.

## '503 Service Temporarily Unavailable'

You might see this when accessing the dashboard URL, and this is typically
an error response from the Application Load Balancer. Make sure you have
followed the instructions in the notebook, and waited a few minutes for the
Amazon ECS Service to start. You might need to check your Amazon ECS Tasks
if this error message doesn't disappear after 5 minutes of waiting.

## 'An error was encountered with the requested page.'

You might see this if you are using a custom domain (or subdomain). Check that
the Callback URL on the Amazon Cognito User Pool Client matches your domain (or
subdomain) exactly: even capital letters and forgetting the trailing slash can
cause issues here.
