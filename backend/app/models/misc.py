from sqlmodel import Field, SQLModel


# Generic message
class Message(SQLModel):
    """
    Generic message.

    Defines a simple structure for generic messages.

    Args:
        message (str): The content of the message.

    Returns:
        None

    Notes:
        This class can be used for various messaging purposes throughout the application.
    """

    message: str


# JSON payload containing access token
class Token(SQLModel):
    """
    JSON payload containing access token.

    Defines the structure for an authentication token response.

    Args:
        access_token (str): The access token string.
        token_type (str): The type of token, defaults to "bearer".

    Returns:
        None

    Notes:
        This class is used in the authentication process to return token information.
    """

    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    """
    Contents of JWT token.

    Defines the structure for the payload of a JWT token.

    Args:
        sub (str, optional): The subject of the token, usually the user ID.

    Returns:
        None

    Notes:
        This class represents the decoded contents of a JWT token.
    """

    sub: str | None = None


class NewPassword(SQLModel):
    """
    Class for resetting password.

    Defines the structure for a password reset request.

    Args:
        token (str): The token for password reset verification.
        new_password (str): The new password to set, with length constraints.

    Returns:
        None

    Notes:
        This class is used in the password reset process.
    """

    token: str
    new_password: str = Field(min_length=8, max_length=40)
