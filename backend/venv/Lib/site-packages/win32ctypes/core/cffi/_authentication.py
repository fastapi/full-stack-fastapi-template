#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from weakref import WeakKeyDictionary

from win32ctypes.core.compat import is_text
from ._util import ffi, check_false, dlls
from ._nl_support import _GetACP
from ._common import _PyBytes_FromStringAndSize


ffi.cdef("""

typedef struct _FILETIME {
  DWORD dwLowDateTime;
  DWORD dwHighDateTime;
} FILETIME, *PFILETIME;

typedef struct _CREDENTIAL_ATTRIBUTE {
  LPWSTR Keyword;
  DWORD  Flags;
  DWORD  ValueSize;
  LPBYTE Value;
} CREDENTIAL_ATTRIBUTE, *PCREDENTIAL_ATTRIBUTE;

typedef struct _CREDENTIAL {
  DWORD                 Flags;
  DWORD                 Type;
  LPWSTR                TargetName;
  LPWSTR                Comment;
  FILETIME              LastWritten;
  DWORD                 CredentialBlobSize;
  LPBYTE                CredentialBlob;
  DWORD                 Persist;
  DWORD                 AttributeCount;
  PCREDENTIAL_ATTRIBUTE Attributes;
  LPWSTR                TargetAlias;
  LPWSTR                UserName;
} CREDENTIAL, *PCREDENTIAL;


BOOL WINAPI CredReadW(
    LPCWSTR TargetName, DWORD Type, DWORD Flags, PCREDENTIAL *Credential);
BOOL WINAPI CredWriteW(PCREDENTIAL Credential, DWORD);
VOID WINAPI CredFree(PVOID Buffer);
BOOL WINAPI CredDeleteW(LPCWSTR TargetName, DWORD Type, DWORD Flags);
BOOL WINAPI CredEnumerateW(
    LPCWSTR Filter, DWORD Flags, DWORD *Count, PCREDENTIAL **Credential);
""")

_keep_alive = WeakKeyDictionary()


SUPPORTED_CREDKEYS = set((
    u'Type', u'TargetName', u'Persist',
    u'UserName', u'Comment', u'CredentialBlob'))


def make_unicode(password):
    """ Convert the input string to unicode.

    """
    if is_text(password):
        return password
    else:
        code_page = _GetACP()
        return password.decode(encoding=str(code_page), errors='strict')


class _CREDENTIAL(object):

    def __call__(self):
        return ffi.new("PCREDENTIAL")[0]

    @classmethod
    def fromdict(cls, credential, flag=0):
        unsupported = set(credential.keys()) - SUPPORTED_CREDKEYS
        if len(unsupported):
            raise ValueError("Unsupported keys: {0}".format(unsupported))
        if flag != 0:
            raise ValueError("flag != 0 not yet supported")

        factory = cls()
        c_creds = factory()
        # values to ref and make sure that they will not go away
        values = []
        for key, value in credential.items():
            if key == u'CredentialBlob':
                blob = make_unicode(value)
                blob_data = ffi.new('wchar_t[]', blob)
                # new adds a NULL at the end that we do not want.
                c_creds.CredentialBlobSize = \
                    ffi.sizeof(blob_data) - ffi.sizeof('wchar_t')
                c_creds.CredentialBlob = ffi.cast('LPBYTE', blob_data)
                values.append(blob_data)
            elif key in (u'Type', u'Persist'):
                setattr(c_creds, key, value)
            elif value is None:
                setattr(c_creds, key, ffi.NULL)
            else:
                blob = make_unicode(value)
                pblob = ffi.new('wchar_t[]', blob)
                values.append(pblob)
                setattr(c_creds, key, ffi.cast('LPTSTR', pblob))
        # keep values alive until c_creds goes away.
        _keep_alive[c_creds] = tuple(values)
        return c_creds


CREDENTIAL = _CREDENTIAL()


def PCREDENTIAL(value=None):
    return ffi.new("PCREDENTIAL", ffi.NULL if value is None else value)


def PPCREDENTIAL(value=None):
    return ffi.new("PCREDENTIAL*", ffi.NULL if value is None else value)


def PPPCREDENTIAL(value=None):
    return ffi.new("PCREDENTIAL**", ffi.NULL if value is None else value)


def credential2dict(pc_creds):
    credentials = {}
    for key in SUPPORTED_CREDKEYS:
        if key == u'CredentialBlob':
            data = _PyBytes_FromStringAndSize(
                pc_creds.CredentialBlob, pc_creds.CredentialBlobSize)
        elif key in (u'Type', u'Persist'):
            data = int(getattr(pc_creds, key))
        else:
            string_pointer = getattr(pc_creds, key)
            if string_pointer == ffi.NULL:
                data = None
            else:
                data = ffi.string(string_pointer)
        credentials[key] = data
    return credentials


def _CredRead(TargetName, Type, Flags, ppCredential):
    target = make_unicode(TargetName)
    return check_false(
        dlls.advapi32.CredReadW(target, Type, Flags, ppCredential),
        u'CredRead')


def _CredWrite(Credential, Flags):
    return check_false(
        dlls.advapi32.CredWriteW(Credential, Flags), u'CredWrite')


def _CredDelete(TargetName, Type, Flags):
    return check_false(
        dlls.advapi32.CredDeleteW(
            make_unicode(TargetName), Type, Flags), u'CredDelete')


def _CredEnumerate(Filter, Flags, Count, pppCredential):
    filter = make_unicode(Filter) if Filter is not None else ffi.NULL
    return check_false(
        dlls.advapi32.CredEnumerateW(filter, Flags, Count, pppCredential),
        u'CredEnumerate')


_CredFree = dlls.advapi32.CredFree
