import os
import pytest
from starlette.testclient import TestClient
import glob

from app.main import app


@pytest.fixture(scope="session")
def test_app():
    client = TestClient(app)
    yield client 

    sig_files = glob.glob('tests/files/*.sig')
    for file in sig_files:
        os.remove(file)

@pytest.fixture(scope="session")
def test_license():
    return os.getenv("license_crypto_pro")

@pytest.fixture(scope="session")
def test_api_key():
    return os.getenv("api_key")

@pytest.fixture(scope="session")
def test_all_data():
    all_data = [
        {
            'type': 'file',
            'value': 'tests/files/test1.pdf',
            'hash': '7EA116C69AB1DB88C5601B810BDF2FCDE035C5330395D4FEE9B8CCA03407EA74',
            'sign_attach': {
                'file': '',
                'string': ''
            },
            'sign_deattach': {
                'file': '',
                'string': ''
            },
            'sign_hash': {
                'file': '',
                'string': ''
            }
        },
        {
            'type': 'file',
            'value': 'tests/files/test2.pdf',
            'hash': 'BB197D3844347EC6F4FD5D7CF126B7DCF93455F9DD79CD1E84E7AF6F77BD0780',
            'sign_attach': {
                'file': '',
                'string': ''
            },
            'sign_deattach': {
                'file': '',
                'string': ''
            },
            'sign_hash': {
                'file': '',
                'string': ''
            }
        },

        {
            'type': 'string',
            'value': "{'message': 'Привет мир!!!'}",
            'hash': 'AEB083926318FC7F48D229187FCBB0C881A389E7F548353585962E17EA890216',
            'sign_attach': {
                'file': '',
                'string': ''
            },
            'sign_deattach': {
                'file': '',
                'string': ''
            },
            'sign_hash': {
                'file': '',
                'string': ''
            }
        },

        {
            'type': 'string',
            'value': "{'message': 'Привет война!!!'}",
            'hash': 'BBB8FD8699C905ED730C0456F7511B9AC62BAEC53E541D553D4F7AF64975720A',
            'sign_attach': {
                'file': '',
                'string': ''
            },
            'sign_deattach': {
                'file': '',
                'string': ''
            },
            'sign_hash': {
                'file': '',
                'string': ''
            }
        },
        {
            'type': 'xml',
            'value': 'tests/files/test.xml',
            'hash': 'AD140D96A03E6141B7E7A4F9392CDC551C1A80E6B3C258D6D1DC16B86630414B',
            'sign_attach': {
                'file': '',
                'string': ''
            },
            'sign_deattach': {
                'file': '',
                'string': ''
            },
            'sign_hash': {
                'file': '',
                'string': ''
            }
        },
        
    ]
    return all_data

@pytest.fixture(scope="session")
def test_files_data(test_all_data):
    files_data = [f for f in test_all_data if f['type'] == 'file']
    return files_data

@pytest.fixture(scope="session")
def test_strings_data(test_all_data):
    strings_data = [f for f in test_all_data if f['type'] == 'string']
    return strings_data

@pytest.fixture(scope="session")
def test_xml_data(test_all_data):
    xml_data = [f for f in test_all_data if f['type'] == 'xml']
    return xml_data

@pytest.fixture(scope="session")
def path_to_cert_file():
    return "tests/files/test.cer"

@pytest.fixture(scope="session")
def thumbprint():
    return "A8C8C3222A319536F7C2E240DB81D18EF87D4CAB"

