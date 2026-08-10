from pathlib import Path
import json

# Update the .env file with the answers from the .copier-answers.yml file
# without using Jinja2 templates in the .env file, this way the code works as is
# without needing Copier, but if Copier is used, the .env file will be updated
root_path = Path(__file__).parent.parent
answers_path = Path(__file__).parent / ".copier-answers.yml"
answers = json.loads(answers_path.read_text())
env_path = root_path / ".env"
env_content = env_path.read_text()
# Keep deployment provider settings from replacing local development defaults.
env_answer_keys = {
    "emails_from_email",
    "first_superuser",
    "first_superuser_password",
    "postgres_password",
    "project_name",
    "secret_key",
}
lines = []
for line in env_content.splitlines():
    for key, value in answers.items():
        if key not in env_answer_keys:
            continue
        upper_key = key.upper()
        if line.startswith(f"{upper_key}="):
            if " " in value:
                content = f"{upper_key}={value!r}"
            else:
                content = f"{upper_key}={value}"
            new_line = line.replace(line, content)
            lines.append(new_line)
            break
    else:
        lines.append(line)
env_path.write_text("\n".join(lines))
