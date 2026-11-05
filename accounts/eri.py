"""ERI / E-IMZO login checks.

The browser signs a one-time challenge with the local E-IMZO app.
This module checks that the PKCS#7 really contains that challenge and that
the signature matches the certificate inside it.

GOST keys, which are the usual Uzbekistan ERI keys, are accepted only when
E-IMZO-SERVER confirms them (chain and OCSP). RSA and ECDSA keys are checked
here directly.
"""

from __future__ import annotations

import base64
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone

from asn1crypto import cms, x509 as asn1_x509
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from django.conf import settings

TIN_OID = '1.2.860.3.16.1.1'
PINFL_OID = '1.2.860.3.16.1.2'
MESSAGE_DIGEST_OID = '1.2.840.113549.1.9.4'
DIGESTS = {
    '2.16.840.1.101.3.4.2.1': 'sha256',
    '1.3.14.3.2.26': 'sha1',
    '1.2.840.113549.1.1.11': 'sha256',
    '1.2.840.113549.1.1.5': 'sha1',
}


class EriError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def issue_challenge() -> str:
    if settings.EIMZO_SERVER_URL:
        url = settings.EIMZO_SERVER_URL.rstrip('/') + '/frontend/challenge'
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise EriError('server_unreachable') from exc
        if payload.get('status') != 1 or not payload.get('challenge'):
            raise EriError('server_rejected')
        return str(payload['challenge'])
    import secrets
    return secrets.token_urlsafe(24)


def verify_login(pkcs7_b64: str, challenge: str, request) -> dict:
    info = _parse_pkcs7(pkcs7_b64, challenge)
    if settings.EIMZO_SERVER_URL:
        server_info = _verify_with_server(pkcs7_b64, request)
        subject = (server_info.get('subjectCertificateInfo') or {}).get('subjectName') or {}
        info['cn'] = info['cn'] or str(subject.get('CN') or '')
        info['stir'] = info['stir'] or _digits(subject.get(TIN_OID) or subject.get('TIN'))
        info['pinfl'] = info['pinfl'] or _digits(subject.get(PINFL_OID) or subject.get('UID'))
        info['verified_by'] = 'eimzo-server'
    else:
        _verify_signature(info)
        info['verified_by'] = 'local-signature'
    if not info['cn'] and not info['stir'] and not info['pinfl']:
        raise EriError('identity_missing')
    return info


def _parse_pkcs7(pkcs7_b64: str, challenge: str) -> dict:
    try:
        der = base64.b64decode(pkcs7_b64, validate=True)
        content_info = cms.ContentInfo.load(der)
    except Exception as exc:
        raise EriError('bad_pkcs7') from exc
    if content_info['content_type'].native != 'signed_data':
        raise EriError('bad_pkcs7')
    signed = content_info['content']
    encapsulated = signed['encap_content_info']['content']
    if encapsulated is None:
        raise EriError('bad_pkcs7')
    content = encapsulated.native
    if isinstance(content, str):
        content = content.encode('utf-8')
    try:
        text = content.decode('utf-8').strip()
    except UnicodeDecodeError as exc:
        raise EriError('challenge_mismatch') from exc
    if text != challenge:
        raise EriError('challenge_mismatch')
    signer = signed['signer_infos'][0]
    cert = _signer_certificate(signed, signer)
    identity = _identity(cert)
    _check_dates(cert)
    return {
        'content': content,
        'signed': signed,
        'signer': signer,
        'cert_der': cert.dump(),
        'serial': format(cert.serial_number, 'x'),
        'valid_to': _as_utc(cert.not_valid_after).strftime('%d.%m.%Y'),
        **identity,
    }


def _signer_certificate(signed, signer):
    sid = signer['sid']
    serial = None
    if sid.name == 'issuer_and_serial_number':
        serial = sid.chosen['serial_number'].native
    for item in signed['certificates']:
        cert = item.chosen
        if not isinstance(cert, asn1_x509.Certificate):
            continue
        if serial is None or cert.serial_number == serial:
            return cert
    raise EriError('bad_pkcs7')


def _identity(cert: asn1_x509.Certificate) -> dict:
    values = {}
    for rdn in cert.subject.chosen:
        for attr in rdn:
            native = attr['value'].native
            if isinstance(native, bytes):
                continue
            values[attr['type'].dotted] = str(native)
            values[str(attr['type'].native)] = str(native)
    stir = _digits(values.get(TIN_OID) or values.get('serial_number') or values.get('tin'))
    pinfl = _digits(values.get(PINFL_OID) or values.get('uid'))
    if stir and len(stir) == 14 and not pinfl:
        pinfl, stir = stir, ''
    if pinfl and len(pinfl) == 9 and not stir:
        stir, pinfl = pinfl, ''
    return {
        'cn': values.get('common_name') or values.get('CN') or '',
        'stir': stir if len(stir) == 9 else '',
        'pinfl': pinfl if len(pinfl) == 14 else '',
    }


def _digits(value) -> str:
    return ''.join(ch for ch in str(value or '') if ch.isdigit())


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _check_dates(cert: asn1_x509.Certificate) -> None:
    now = datetime.now(timezone.utc)
    if now < _as_utc(cert.not_valid_before) or now > _as_utc(cert.not_valid_after):
        raise EriError('cert_expired')


def _verify_signature(info: dict) -> None:
    signer = info['signer']
    signature_oid = signer['signature_algorithm']['algorithm'].dotted
    if signature_oid.startswith('1.2.860.'):
        raise EriError('gost_needs_server')
    digest_oid = signer['digest_algorithm']['algorithm'].dotted
    digest_name = DIGESTS.get(digest_oid) or DIGESTS.get(signature_oid)
    if digest_name is None:
        raise EriError('gost_needs_server')
    signed_attrs = signer['signed_attrs']
    if signed_attrs is not None:
        digest = getattr(hashlib, digest_name)(info['content']).digest()
        found = None
        for attr in signed_attrs:
            if attr['type'].dotted == MESSAGE_DIGEST_OID:
                found = attr['values'][0].native
        if found != digest:
            raise EriError('signature_invalid')
        payload = b'\x31' + signed_attrs.dump()[1:]
    else:
        payload = info['content']
    cert = x509.load_der_x509_certificate(info['cert_der'])
    public_key = cert.public_key()
    hash_alg = hashes.SHA256() if digest_name == 'sha256' else hashes.SHA1()
    try:
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signer['signature'].native, payload, ec.ECDSA(hash_alg))
        else:
            public_key.verify(signer['signature'].native, payload, padding.PKCS1v15(), hash_alg)
    except (InvalidSignature, TypeError, ValueError) as exc:
        raise EriError('signature_invalid') from exc


def _verify_with_server(pkcs7_b64: str, request) -> dict:
    url = settings.EIMZO_SERVER_URL.rstrip('/') + '/backend/auth'
    host = request.get_host().split(':')[0]
    ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or '127.0.0.1'
    req = urllib.request.Request(
        url,
        data=pkcs7_b64.encode('ascii'),
        headers={'X-Real-IP': ip, 'Host': host, 'Content-Type': 'text/plain'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise EriError('server_rejected') from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EriError('server_unreachable') from exc
    if payload.get('status') != 1:
        raise EriError('server_rejected')
    return payload
