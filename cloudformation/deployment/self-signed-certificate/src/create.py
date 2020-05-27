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

# runtime install
tmp_path = Path(tempfile.gettempdir())
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "--target={}".format(tmp_path),
    "cryptography"
])
sys.path.append(str(tmp_path))
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


helper = CfnResource()


def generate_key():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return key


def generate_self_signed_certificate(key):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"example.com")
    ])
    cert = x509.CertificateBuilder()
    cert = cert.subject_name(subject)
    cert = cert.issuer_name(issuer)
    cert = cert.public_key(key.public_key())
    cert = cert.serial_number(x509.random_serial_number())
    cert = cert.not_valid_before(datetime.utcnow())
    cert = cert.not_valid_after(datetime.utcnow() + timedelta(days=365))
    cert = cert.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    )
    cert = cert.sign(key, hashes.SHA256(), default_backend())
    return cert


def acm_import_certificate(cert, key):
    acm_client = boto3.client('acm')
    cert_bytes = cert.public_bytes(
        encoding=serialization.Encoding.PEM
    )
    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    response = acm_client.import_certificate(
        Certificate=cert_bytes,
        PrivateKey=key_bytes
    )
    return response['CertificateArn']


@helper.create
def on_create(event, _):
    key = generate_key()
    cert = generate_self_signed_certificate(key)
    cert_arn = acm_import_certificate(cert, key)
    return cert_arn


@helper.update
def on_update(_, __):
    pass


@helper.delete
def on_delete(event, __):
    pass


def handler(event, context):
    helper(event, context)
