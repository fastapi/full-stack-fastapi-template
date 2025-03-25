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
    'asn1_build',
    'asn1_parse',
    'ASN1FormatError',
    'BIT_STRING',
    'INTEGER',
    'SEQUENCE',
    'OBJECT_IDENTIFIER',
    'OCTET_STRING',
    'NULL',
    ]

INTEGER = 0x02
BIT_STRING = 0x03
OCTET_STRING = 0x04
NULL = 0x05
OBJECT_IDENTIFIER = 0x06
SEQUENCE = 0x30


class ASN1FormatError(Exception):
    pass


def asn1_parse(template, data):
    """Parse a data structure according to an ASN.1 template.

    @param template: tuples comprising the ASN.1 template
    @param data: byte string data to parse
    @return: decoded structure
    """
    data = bytearray(data)
    r = []
    i = 0
    try:
      for t in template:
          tag = data[i]
          i += 1
          if tag == t[0]:
              length = data[i]
              i += 1
              if length & 0x80:
                  n = length & 0x7f
                  length = 0
                  for j in range(n):
                      length = (length << 8) | data[i]
                      i += 1
              if tag == INTEGER:
                  n = 0
                  for j in range(length):
                      n = (n << 8) | data[i]
                      i += 1
                  r.append(n)
              elif tag == BIT_STRING:
                  r.append(data[i:i+length])
                  i += length
              elif tag == NULL:
                  assert length == 0
                  r.append(None)
              elif tag == OBJECT_IDENTIFIER:
                  r.append(data[i:i+length])
                  i += length
              elif tag == SEQUENCE:
                  r.append(asn1_parse(t[1], data[i:i+length]))
                  i += length
              else:
                  raise ASN1FormatError(
                      "Unexpected tag in template: %02x" % tag)
          else:
              raise ASN1FormatError(
                  "Unexpected tag (got %02x, expecting %02x)" % (tag, t[0]))
      return r
    except IndexError:
      raise ASN1FormatError("Data truncated at byte %d"%i)

def asn1_length(n):
    """Return a string representing a field length in ASN.1 format.

    @param n: integer field length
    @return: ASN.1 field length
    """
    assert n >= 0
    if n < 0x7f:
        return bytearray([n])
    r = bytearray()
    while n > 0:
        r.insert(n & 0xff)
        n >>= 8
    return r


def asn1_encode(type, data):
    length = asn1_length(len(data))
    length.insert(0, type)
    length.extend(data)
    return length


def asn1_build(node):
    """Build a DER-encoded ASN.1 data structure.

    @param node: (type, data) tuples comprising the ASN.1 structure
    @return: DER-encoded ASN.1 byte string
    """
    if node[0] == OCTET_STRING:
        return asn1_encode(OCTET_STRING, node[1])
    if node[0] == NULL:
        assert node[1] is None
        return asn1_encode(NULL, b'')
    elif node[0] == OBJECT_IDENTIFIER:
        return asn1_encode(OBJECT_IDENTIFIER, node[1])
    elif node[0] == SEQUENCE:
        r = bytearray()
        for x in node[1]:
            r += asn1_build(x)
        return asn1_encode(SEQUENCE, r)
    else:
        raise ASN1FormatError("Unexpected tag in template: %02x" % node[0])
