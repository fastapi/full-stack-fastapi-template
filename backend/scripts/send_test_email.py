#!/usr/bin/env python3
"""Send a test email using SMTP settings from environment or ../.env.

Usage:
  # with venv active, from repo root
  python backend/scripts/send_test_email.py --to you@example.com

Options:
  --to     recipient email (defaults to FIRST_SUPERUSER or EMAILS_FROM_EMAIL)
  --subject optional subject
  --body   optional plain text body
"""

from __future__ import annotations

import argparse
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def parse_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        data[k.strip()] = v
    return data


def load_settings() -> dict[str, str]:
    env = dict(os.environ)
    # look for repo root .env (two parents up: backend/scripts -> backend -> repo)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    dotenv = repo_root / ".env"
    file_vars = parse_dotenv(dotenv)
    # prefer environment variables, fallback to file
    merged = {**file_vars, **env}
    return merged


def send(
    smtp_host: str,
    smtp_port: int,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
    use_tls: bool = False,
    use_ssl: bool = False,
    user: str | None = None,
    password: str | None = None,
):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    if use_ssl:
        smtp = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
    else:
        smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    with smtp:
        smtp.ehlo()
        if use_tls and not use_ssl:
            smtp.starttls()
            smtp.ehlo()
        if user:
            smtp.login(user, password or "")
        smtp.send_message(msg)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--to", help="Recipient email")
    p.add_argument("--subject", default="Test email from full-stack-fastapi-template")
    p.add_argument("--body", default="This is a test email sent to Mailpit.")
    args = p.parse_args()

    cfg = load_settings()

    smtp_host = cfg.get("SMTP_HOST") or "localhost"
    smtp_port = int(cfg.get("SMTP_PORT") or 1025)
    smtp_tls = str(cfg.get("SMTP_TLS", "False")).lower() in ("true", "1", "yes")
    smtp_ssl = str(cfg.get("SMTP_SSL", "False")).lower() in ("true", "1", "yes")
    smtp_user = cfg.get("SMTP_USER") or None
    smtp_password = cfg.get("SMTP_PASSWORD") or None

    sender = (
        cfg.get("EMAILS_FROM_EMAIL")
        or cfg.get("FIRST_SUPERUSER")
        or "noreply@example.com"
    )
    recipient = args.to or cfg.get("FIRST_SUPERUSER") or sender

    print(
        f"Sending test email to {recipient} via {smtp_host}:{smtp_port} (tls={smtp_tls} ssl={smtp_ssl})"
    )
    try:
        send(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            sender=sender,
            recipient=recipient,
            subject=args.subject,
            body=args.body,
            use_tls=smtp_tls,
            use_ssl=smtp_ssl,
            user=smtp_user,
            password=smtp_password,
        )
    except Exception as e:
        print("Failed to send email:", e)
        raise SystemExit(1) from e
    print("Email sent — check Mailpit UI at http://localhost:8025")


if __name__ == "__main__":
    main()
