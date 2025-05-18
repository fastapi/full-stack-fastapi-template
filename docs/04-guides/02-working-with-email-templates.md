# Working with Email Templates

This guide explains how to work with email templates in the Full Stack FastAPI Template.

## Overview

The template uses [MJML](https://mjml.io/) for creating responsive email templates that look good across different email clients. MJML is a markup language designed to reduce the pain of coding responsive emails.

## Email Templates Structure

Email templates are located in the `backend/app/email-templates/` directory:

```
backend/app/email-templates/
├── build/              # Contains compiled HTML templates
│   ├── new_account.html
│   ├── reset_password.html
│   └── test_email.html
└── src/                # Contains source MJML templates
    ├── new_account.mjml
    ├── reset_password.mjml
    └── test_email.mjml
```

## Available Templates

The template includes the following email templates:

1. **new_account.mjml**: Sent when a new user account is created
2. **reset_password.mjml**: Sent when a user requests a password reset
3. **test_email.mjml**: Used for testing the email functionality

## Creating and Modifying Templates

### Prerequisites

To work with MJML templates, you need Node.js and the MJML package:

```bash
# Install MJML globally
npm install -g mjml
```

### Editing an Existing Template

1. Edit the MJML file in the `src/` directory
2. Compile the MJML to HTML:

```bash
cd backend/app/email-templates
mjml src/template_name.mjml -o build/template_name.html
```

### Creating a New Template

1. Create a new MJML file in the `src/` directory:

```bash
touch backend/app/email-templates/src/my_template.mjml
```

2. Edit the file with your template content:

```html
<mjml>
  <mj-head>
    <mj-title>My Template</mj-title>
    <mj-attributes>
      <mj-all font-family="'Helvetica Neue', Helvetica, Arial, sans-serif"></mj-all>
      <mj-text font-weight="400" font-size="16px" color="#000000" line-height="24px"></mj-text>
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding-bottom="20px" padding-top="20px">
      <mj-column width="100%">
        <mj-image src="https://mydomain.com/logo.png" alt="Logo" align="center" width="100px"></mj-image>
      </mj-column>
    </mj-section>
    <mj-section background-color="#ffffff" padding-bottom="0px" padding-top="0">
      <mj-column width="100%">
        <mj-text align="center" font-size="20px" font-weight="bold">
          My Email Title
        </mj-text>
        <mj-divider border-color="#A9A9A9" border-width="1px" border-style="dashed" padding-left="100px" padding-right="100px" padding-bottom="20px" padding-top="20px"></mj-divider>
      </mj-column>
    </mj-section>
    <mj-section background-color="#ffffff" padding-bottom="20px" padding-top="20px">
      <mj-column>
        <mj-text>
          Hello {{ username }},
        </mj-text>
        <mj-text>
          This is my custom email template with a variable: {{ my_variable }}.
        </mj-text>
        <mj-text>
          Best regards,<br />
          My Company
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

3. Compile the MJML to HTML:

```bash
cd backend/app/email-templates
mjml src/my_template.mjml -o build/my_template.html
```

## Using Templates in the Code

The email templates are used in the `EmailService` class:

```python
# app/modules/email/services/email_service.py
def send_email(
    self,
    email_to: str,
    subject: str,
    template_type: EmailTemplateType,
    template_data: Dict[str, Any],
) -> bool:
    """Send email using template."""
    template_path = self._get_template_path(template_type)
    html_content = self._render_template(template_path, template_data)
    return self._send_email(email_to, subject, html_content)
```

The available template types are defined in an enum:

```python
# app/modules/email/domain/models.py
class EmailTemplateType(str, Enum):
    """Email template types."""
    NEW_ACCOUNT = "new_account"
    RESET_PASSWORD = "reset_password"
    TEST_EMAIL = "test_email"
    # Add your new template type here
    MY_TEMPLATE = "my_template"
```

## Template Variables

Each template supports specific variables that can be passed in the `template_data` dictionary:

### new_account.mjml

- `username`: The user's name or email
- `project_name`: The name of the project

### reset_password.mjml

- `username`: The user's name or email
- `valid_hours`: Number of hours the reset token is valid for
- `project_name`: The name of the project
- `link`: The password reset link

### test_email.mjml

- `test_email`: The test email address

### Adding Custom Variables

To add custom variables to a template:

1. Use the `{{ variable_name }}` syntax in your MJML template
2. Pass the variable in the `template_data` dictionary when sending the email

```python
success = email_service.send_email(
    email_to=user.email,
    subject="My Custom Email",
    template_type=EmailTemplateType.MY_TEMPLATE,
    template_data={
        "username": user.full_name or user.email,
        "my_variable": "This is a custom value",
    },
)
```

## Best Practices

1. **Keep Templates Simple**: Email clients have limited CSS support
2. **Test on Multiple Clients**: Test templates on various email clients
3. **Use MJML Components**: MJML provides many responsive components
4. **Maintain Consistency**: Use consistent styling across all templates
5. **Use Variables**: Use template variables instead of hardcoding values
6. **Consider Plain Text**: Always provide a plain text alternative for accessibility

## Testing Email Templates

### Testing Rendering

To test template rendering:

```python
# In a test file
from app.modules.email.services.email_service import EmailService
from app.modules.email.domain.models import EmailTemplateType

def test_render_template():
    email_service = EmailService()
    template_path = email_service._get_template_path(EmailTemplateType.NEW_ACCOUNT)
    html_content = email_service._render_template(
        template_path,
        {
            "username": "test_user",
            "project_name": "Test Project",
        },
    )

    # Assert content contains expected values
    assert "test_user" in html_content
    assert "Test Project" in html_content
```

### Testing Email Sending

For testing email sending in development:

1. Use Docker Compose to run MailHog:

```yaml
# In docker-compose.yml
services:
  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP server
      - "8025:8025"  # Web UI
```

2. Configure the application to use MailHog:

```
# In .env
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_TLS=false
```

3. Access MailHog web UI at http://localhost:8025 to see sent emails

## MJML Resources

- [MJML Documentation](https://documentation.mjml.io/)
- [MJML Components](https://documentation.mjml.io/#components)
- [MJML Try It Live](https://mjml.io/try-it-live)
- [MJML App](https://mjmlio.github.io/mjml-app/) (Desktop app for Windows, macOS, and Linux)