import sys
from pathlib import Path


files_to_ignore_text = '''
# Warning! Files in the below section contain your credentials!
# Credentials should never be pushed to the repository.
cookiecutter-config-file.yml
*.env
'''

gitignore = Path("./.gitignore")
if not gitignore.exists():
    # We should assume this file exists otherwise something went wrong
    sys.exit(1)

existing_gitignore_text = gitignore.read_text()
gitignore.write_text(existing_gitignore_text + files_to_ignore_text)

sys.exit(0)
