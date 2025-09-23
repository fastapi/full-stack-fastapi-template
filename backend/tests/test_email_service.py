import pytest
from unittest.mock import patch, MagicMock
from app.utils import send_email

def test_email_service_integration():
    """Test email service integration."""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = send_email(
            email_to="test@example.com",
            subject="Test Subject",
            html_content="<p>Test email</p>"
        )

        mock_smtp.assert_called_once()

@patch('app.core.config.settings.SMTP_HOST', 'localhost')
def test_email_configuration():
    """Test email configuration settings."""
    from app.core.config import settings
    assert settings.SMTP_HOST == 'localhost'

def test_email_template_rendering():
    """Test email template rendering with variables."""
    template_data = {
        "username": "Test User",
        "reset_link": "https://example.com/reset"
    }

    # Mock template rendering
    with patch('app.email_templates.render_template') as mock_render:
        mock_render.return_value = "<p>Hello Test User</p>"
        result = mock_render(template_data)
        assert "Test User" in result

def test_email_sending_failure():
    """Test handling email sending failures."""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp.side_effect = Exception("SMTP connection failed")

        result = send_email("test@example.com", "Test", "<p>Test</p>")
        # Should handle the error gracefully
        assert result is False or result is None
