# Customization Guide

## Customizing the AWS CloudFormation template

Our AWS CloudFormation template contains a number of custom resources, and each custom resource is backed by an AWS Lambda function. When creating each AWS Lambda function we need to have already downloaded its dependencies and packages them into a single zip file. So let's first download the dependencies for each AWS Lambda function into the their respective `src` directories.

```bash
(cd ./cloudformation/deployment/self-signed-certificate/ && \
pip install -r requirements.txt -t ./src/site-packages)
(cd ./cloudformation/deployment/string-functions/ && \
pip install -r requirements.txt -t ./src/site-packages)
(cd ./cloudformation/assistants/solution-assistant && \
pip install -r requirements.txt -t ./src/site-packages)
(cd ./cloudformation/assistants/bucket-assistant && \
pip install -r requirements.txt -t ./src/site-packages)
```

Using the AWS Command Line Interface, we have a useful function called `package` that helps upload the AWS Lambda function's code and also any AWS CloudFormation nested stacks too. Make sure you replace `<s3-bucket>` and `<s3-prefix>` with an Amazon S3 bucket that you have created in your account.

```bash
aws --region us-west-2 cloudformation package \
--template-file ./cloudformation/template.yaml \
--s3-bucket <s3-bucket> \
--s3-prefix <s3-prefix> \
--output-template-file ./build/packaged.yaml
```

Add `--debug` if you have any issues at this stage. You can then use the `deploy` function to create the stack.

```bash
aws cloudformation deploy \
--stack-name sagemaker-ml-dashboards \
--template-file ./build/packaged.yaml \
--capabilities CAPABILITY_IAM \
```

Sometimes you'll want to override the default parameters so add the following argument in that case (e.g. for a custom `ApplicationLoadBalancerSSLCertificate` replace `<certificate-arn>` with your ACM Certificate ARN):

```bash
--parameter-overrides ApplicationLoadBalancerSSLCertificate=<certificate-arn>
```

Any issues at this stage should be debugged by disabling AWS CloudFormation stack rollback and the `create-stack` command should be used instead of `deploy`.

```bash
aws --region us-west-2 cloudformation create-stack \
--stack-name sagemaker-ml-dashboards \
--template-body file://./build/packaged.yaml \
--capabilities CAPABILITY_IAM \
--disable-rollback \
```

Should you need to use custom parameters with this command, the syntax is slightly different. Add:

```bash
--parameters \
ParameterKey=ResourceName,ParameterValue=<stack-name> \
ParameterKey=CognitoAuthenticationSampleUserEmail,ParameterValue=<email>
```

When you have your AWS CloudFormation stack deployed, use the code found in the notebook to build, push and deploy your Docker image.

## Customizing the Amazon SageMaker Notebook Instance

### Custom Conda Environment Dependencies

Separate from the dependencies required inside the model or dashboard Docker
containers, you may want to use certain libraries and packages on the Amazon
SageMaker Notebook Instance (e.g. from within Jupyter notebooks). As an example,
in this solution we use the `transformers` library from inside the notebook to
download a pre-trained model. And we also use certain development tools such as
`pip-tools`, `flake8` and `pytest`. You can add custom dependencies to
`requirements.dev.txt` (or `requirements.dev.in` and then use `pip-compile`).
Our solution uses a custom Conda environment called `dashboard` (using Python
3.6), and each time the Amazon SageMaker Notebook Instance is started these
requirements will be installed. See the OnStart Lifecycle Configuration for
implementation details.

### IAM Roles & Policies

As a best practice for security, the Amazon SageMaker Notebook Instance has
an execution role (i.e. IAM Role) with a minimal IAM Policy. Only actions
performed by the example notebooks are allowed, and only on resources that
were created as part of the solution. You might find this limiting when
customizing the solution. You can add actions as needed or attach a less
restrictive IAM Policy (such as the managed policy called
`AmazonSageMakerFullAccess`) to the notebook's execution role.
