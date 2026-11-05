import base64
import json
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from django.test import Client, TestCase


def signed_pkcs7(challenge, stir='305556789', pinfl='12345678901234', cn='RAHIMOV AZIZ'):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    name = x509.Name([
        x509.NameAttribute(x509.NameOID.COMMON_NAME, cn),
        x509.NameAttribute(x509.ObjectIdentifier('1.2.860.3.16.1.1'), stir),
        x509.NameAttribute(x509.ObjectIdentifier('1.2.860.3.16.1.2'), pinfl),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    der = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(challenge.encode('utf-8'))
        .add_signer(cert, key, hashes.SHA256())
        .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.Binary])
    )
    return base64.b64encode(der).decode('ascii')


class EriLoginTests(TestCase):
    def test_rsa_signature_opens_the_session(self):
        client = Client()
        challenge = client.get('/eri/challenge/').json()['challenge']
        response = client.post(
            '/eri/verify/',
            data=json.dumps({'pkcs7': signed_pkcs7(challenge)}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(client.session['eri_authenticated'])
        self.assertEqual(client.session['profile']['stir'], '305556789')
        self.assertEqual(client.session['profile']['company'], 'RAHIMOV AZIZ')

    def test_reused_challenge_is_rejected(self):
        client = Client()
        challenge = client.get('/eri/challenge/').json()['challenge']
        body = json.dumps({'pkcs7': signed_pkcs7(challenge)})
        self.assertEqual(client.post('/eri/verify/', data=body, content_type='application/json').status_code, 200)
        again = client.post('/eri/verify/', data=body, content_type='application/json')
        self.assertEqual(again.status_code, 400)
        self.assertEqual(again.json()['error'], 'challenge_expired')

    def test_different_challenge_is_rejected(self):
        client = Client()
        client.get('/eri/challenge/')
        response = client.post(
            '/eri/verify/',
            data=json.dumps({'pkcs7': signed_pkcs7('another-challenge')}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'challenge_mismatch')

    def test_login_page_lists_the_entry(self):
        response = Client().get('/eri/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'eri.js')
