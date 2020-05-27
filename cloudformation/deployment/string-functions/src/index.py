import random
import string
import sys

# import from local site-packages
# flake8: noqa: E402
sys.path.append('./site-packages')
from crhelper import CfnResource


helper = CfnResource()


def random_string(length):
    alphanumeric = string.ascii_lowercase + '0123456789'
    return ''.join(random.choice(alphanumeric) for i in range(length))


@helper.create
@helper.update
def on_create(event, _):
    function = event['ResourceProperties']['Function']
    if function == 'random':
        length = int(event['ResourceProperties']['Length'])
        output_string = random_string(length)
    elif function == 'lower':
        input_string = event['ResourceProperties']['InputString']
        output_string = input_string.lower()
    else:
        raise ValueError('Unsupported function.')
    helper.Data['OutputString'] = output_string


@helper.delete
def on_delete(event, __):
    pass


def handler(event, context):
    helper(event, context)
