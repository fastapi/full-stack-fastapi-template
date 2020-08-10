from app.utils import verify_password_reset_token, generate_password_reset_token


def test_verify_password_reset_token():
    test_email = 'test@myapp.com'
    token = generate_password_reset_token(test_email)
    email = verify_password_reset_token(token)
    assert test_email == email

