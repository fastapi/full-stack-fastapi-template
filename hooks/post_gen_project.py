import sys
from pathlib import Path


files_to_ignore = '''
# Warning! Files in the below section contain your credentials!
# Credentials should never be pushed to the repository.
cookiecutter-config-file.yml
*.env
'''

gitignore = Path("./.gitignore")
if not gitignore.exists():
    # We should assume this file exists otherwise something went wrong
    sys.exit(1)

existing_gitignore = gitignore.read_text()
gitignore.write_text(existing_gitignore + files_to_ignore)

sys.exit(0)
