# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the author be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# Copyright (c) 2008 Greg Hewgill http://hewgill.com
#
# This has been modified from the original software.
# Copyright (c) 2011 William Grant <me@williamgrant.id.au>

__all__ = [
    'DigestTooLargeError',
    'HASH_ALGORITHMS',
    'parse_pem_private_key',
    'parse_private_key',
    'parse_public_key',
    'RSASSA_PKCS1_v1_5_sign',
    'RSASSA_PKCS1_v1_5_verify',
    'UnparsableKeyError',
    ]

import base64
import hashlib
import re

from .asn1 import (
    ASN1FormatError,
    asn1_build,
    asn1_parse,
    BIT_STRING,
    INTEGER,
    SEQUENCE,
    OBJECT_IDENTIFIER,
    OCTET_STRING,
    NULL,
    )


ASN1_Object = [
    (SEQUENCE, [
        (SEQUENCE, [
            (OBJECT_IDENTIFIER,),
            (NULL,),
        ]),
        (BIT_STRING,),
    ])
]

ASN1_RSAPublicKey = [
    (SEQUENCE, [
        (INTEGER,),
        (INTEGER,),
    ])
]

ASN1_RSAPrivateKey = [
    (SEQUENCE, [
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
        (INTEGER,),
    ])
]

HASH_ALGORITHMS = {
    b'rsa-sha1': hashlib.sha1,
    b'rsa-sha256': hashlib.sha256,
    }

# These values come from RFC 3447, section 9.2 Notes, page 43.
HASH_ID_MAP = {
    'sha1': b"\x2b\x0e\x03\x02\x1a",
    'sha256': b"\x60\x86\x48\x01\x65\x03\x04\x02\x01",
    }


class DigestTooLargeError(Exception):
    """The digest is too large to fit within the requested length."""
    pass


class UnparsableKeyError(Exception):
    """The data could not be parsed as a key."""
    pass


def parse_public_key(data):
    """Parse an RSA public key.

    @param data: DER-encoded X.509 subjectPublicKeyInfo
        containing an RFC3447 RSAPublicKey.
    @return: RSA public key
    """
    try:
        # Not sure why the [1:] is necessary to skip a byte.
        x = asn1_parse(ASN1_Object, data)
        pkd = asn1_parse(ASN1_RSAPublicKey, x[0][1][1:])
    except ASN1FormatError as e:
        raise UnparsableKeyError('Unparsable public key: ' + str(e))
    pk = {
        'modulus': pkd[0][0],
        'publicExponent': pkd[0][1],
    }
    return pk


def parse_private_key(data):
    """Parse an RSA private key.

    @param data: DER-encoded RFC3447 RSAPrivateKey.
    @return: RSA private key
    """
    try:
        pka = asn1_parse(ASN1_RSAPrivateKey, data)
    except ASN1FormatError as e:
        raise UnparsableKeyError('Unparsable private key: ' + str(e))
    pk = {
        'version': pka[0][0],
        'modulus': pka[0][1],
        'publicExponent': pka[0][2],
        'privateExponent': pka[0][3],
        'prime1': pka[0][4],
        'prime2': pka[0][5],
        'exponent1': pka[0][6],
        'exponent2': pka[0][7],
        'coefficient': pka[0][8],
    }
    return pk


def parse_pem_private_key(data):
    """Parse a PEM RSA private key.

    @param data: RFC3447 RSAPrivateKey in PEM format.
    @return: RSA private key
    """
    m = re.search(b"--\n(.*?)\n--", data, re.DOTALL)
    if m is None:
        raise UnparsableKeyError("Private key not found")
    try:
        pkdata = base64.b64decode(m.group(1))
    except TypeError as e:
        raise UnparsableKeyError(str(e))
    return parse_private_key(pkdata)


def EMSA_PKCS1_v1_5_encode(hash, mlen):
    """Encode a digest with RFC3447 EMSA-PKCS1-v1_5.

    @param hash: hash object to encode
    @param mlen: desired message length
    @return: encoded digest byte string
    """
    dinfo = asn1_build(
        (SEQUENCE, [
            (SEQUENCE, [
                (OBJECT_IDENTIFIER, HASH_ID_MAP[hash.name.lower()]),
                (NULL, None),
            ]),
            (OCTET_STRING, hash.digest()),
        ]))
    if len(dinfo) + 11 > mlen:
        raise DigestTooLargeError()
    return b"\x00\x01"+b"\xff"*(mlen-len(dinfo)-3)+b"\x00"+dinfo


def str2int(s):
    """Convert a byte string to an integer.

    @param s: byte string representing a positive integer to convert
    @return: converted integer
    """
    s = bytearray(s)
    r = 0
    for c in s:
        r = (r << 8) | c
    return r


def int2str(n, length=-1):
    """Convert an integer to a byte string.

    @param n: positive integer to convert
    @param length: minimum length
    @return: converted bytestring, of at least the minimum length if it was
        specified
    """
    assert n >= 0
    r = bytearray()
    while length < 0 or len(r) < length:
        r.append(n & 0xff)
        n >>= 8
        if length < 0 and n == 0:
            break
    r.reverse()
    assert length < 0 or len(r) == length
    return r


def rsa_decrypt(message, pk, mlen):
    """Perform RSA decryption/signing

    @param message: byte string to operate on
    @param pk: private key data
    @param mlen: desired output length
    @return: byte string result of the operation
    """
    c = str2int(message)

    m1 = pow(c, pk['exponent1'], pk['prime1'])
    m2 = pow(c, pk['exponent2'], pk['prime2'])

    if m1 < m2:
        h = pk['coefficient'] * (m1 + pk['prime1'] - m2) % pk['prime1']
    else:
        h = pk['coefficient'] * (m1 - m2) % pk['prime1']

    return int2str(m2 + h * pk['prime2'], mlen)


def rsa_encrypt(message, pk, mlen):
    """Perform RSA encryption/verification

    @param message: byte string to operate on
    @param pk: public key data
    @param mlen: desired output length
    @return: byte string result of the operation
    """
    m = str2int(message)
    return int2str(pow(m, pk['publicExponent'], pk['modulus']), mlen)


def RSASSA_PKCS1_v1_5_sign(hash, private_key):
    """Sign a digest with RFC3447 RSASSA-PKCS1-v1_5.

    @param hash: hash object to sign
    @param private_key: private key data
    @return: signed digest byte string
    """
    modlen = len(int2str(private_key['modulus']))
    encoded_digest = EMSA_PKCS1_v1_5_encode(hash, modlen)
    return rsa_decrypt(encoded_digest, private_key, modlen)


def RSASSA_PKCS1_v1_5_verify(hash, signature, public_key):
    """Verify a digest signed with RFC3447 RSASSA-PKCS1-v1_5.

    @param hash: hash object to check
    @param signature: signed digest byte string
    @param public_key: public key data
    @return: True if the signature is valid, False otherwise
    """
    modlen = len(int2str(public_key['modulus']))
    encoded_digest = EMSA_PKCS1_v1_5_encode(hash, modlen)
    signed_digest = rsa_encrypt(signature, public_key, modlen)
    return encoded_digest == signed_digest
