from dataclasses import dataclass


@dataclass
class EmailData:
    html_content: str
    subject: str
