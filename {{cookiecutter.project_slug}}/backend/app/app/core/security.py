from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext
from passlib.totp import TOTP
from passlib.exc import TokenError, MalformedTokenError
import uuid

from app.core.config import settings
from app.schemas import NewTOTP

"""
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md
https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Password_Storage_Cheat_Sheet.md
https://blog.cloudflare.com/ensuring-randomness-with-linuxs-random-number-generator/
https://passlib.readthedocs.io/en/stable/lib/passlib.pwd.html
Specifies minimum criteria:
    - Use Argon2id with a minimum configuration of 15 MiB of memory, an iteration count of 2, and 1 degree of parallelism.
    - Passwords shorter than 8 characters are considered to be weak (NIST SP800-63B).
    - Maximum password length of 64 prevents long password Denial of Service attacks.
    - Do not silently truncate passwords.
    - Allow usage of all characters including unicode and whitespace.
"""
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"], deprecated="auto"
)  # current defaults: $argon2id$v=19$m=65536,t=3,p=4, "bcrypt" is deprecated
totp_factory = TOTP.using(secrets={"1": settings.TOTP_SECRET_KEY}, issuer=settings.SERVER_NAME, alg=settings.TOTP_ALGO)


def create_access_token(*, subject: Union[str, Any], expires_delta: timedelta = None, force_totp: bool = False) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode = {"exp": expire, "sub": str(subject), "totp": force_totp}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)
    return encoded_jwt


def create_refresh_token(*, subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    to_encode = {"exp": expire, "sub": str(subject), "refresh": True}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)
    return encoded_jwt


def create_magic_tokens(*, subject: Union[str, Any], expires_delta: timedelta = None) -> list[str]:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    fingerprint = str(uuid.uuid4())
    magic_tokens = []
    # First sub is the user.id, to be emailed. Second is the disposable id.
    for sub in [subject, uuid.uuid4()]:
        to_encode = {"exp": expire, "sub": str(sub), "fingerprint": fingerprint}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)
        magic_tokens.append(encoded_jwt)
    return magic_tokens


def create_new_totp(*, label: str, uri: Optional[str] = None) -> NewTOTP:
    if not uri:
        totp = totp_factory.new()
    else:
        totp = totp_factory.from_source(uri)
    return NewTOTP(
        **{
            "secret": totp.to_json(),
            "key": totp.pretty_key(),
            "uri": totp.to_uri(issuer=settings.SERVER_NAME, label=label),
        }
    )


def verify_totp(*, token: str, secret: str, last_counter: int = None) -> Union[str, bool]:
    """
    token: from user
    secret: totp security string from user in db
    last_counter: int from user in db (may be None)
    """
    try:
        match = totp_factory.verify(token, secret, last_counter=last_counter)
    except (MalformedTokenError, TokenError):
        return False
    else:
        return match.counter


def verify_password(*, plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
