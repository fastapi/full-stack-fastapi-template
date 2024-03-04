from pathlib import Path
import json

def quote_if_needed(value):
    # Convert non-string values to string to check for spaces
    value_str = str(value)
    # Check if the value contains spaces and isn't already quoted
    if ' ' in value_str and not (value_str.startswith('"') and value_str.endswith('"')):
        return f'"{value_str}"'
    return value_str

def main():
    answers_path = Path(__file__).parent / ".copier-answers.yml"
    
    # Load the current answers from the .copier-answers.yml file
    with answers_path.open('r', encoding='utf-8') as file:
        answers = json.loads(file.read())
    
    # Quote the necessary values
    quoted_answers = {key: quote_if_needed(value) for key, value in answers.items()}

    # Write the quoted answers back to the .copier-answers.yml file
    with answers_path.open('w', encoding='utf-8') as file:
        file.write(json.dumps(quoted_answers, indent=4))

if __name__ == "__main__":
    main()
