# Contract: CLI Interface for ERD Generation

## Command: `generate-erd`

### Purpose
Command-line interface for manually generating ERD diagrams from SQLModel definitions.

### Usage
```bash
python -m backend.scripts.generate_erd [options]
```

### Options
- `--models-path PATH`: Path to SQLModel definitions (default: `backend/app/models.py`)
- `--output-path PATH`: Path for generated ERD documentation (default: `docs/database/erd.md`)
- `--validate`: Run validation checks on generated ERD
- `--verbose`: Enable verbose output
- `--help`: Show help message

### Input Requirements
- Valid SQLModel definitions at specified path
- Writable output directory
- Python environment with required dependencies

### Output Specification
- Generated ERD documentation in Markdown format
- Mermaid ERD syntax embedded in code blocks
- Validation report if `--validate` flag used
- Exit code: 0 for success, non-zero for errors

### Error Conditions
- Invalid SQLModel syntax → Exit code 1, error message to stderr
- Missing models file → Exit code 2, error message to stderr
- Unwritable output path → Exit code 3, error message to stderr
- Validation failures → Exit code 4, validation report to stdout

### Success Criteria
- ERD diagram generated successfully
- Output file created and writable
- Mermaid syntax valid and renderable
- All validation checks pass (if requested)

## Command: `validate-erd`

### Purpose
Validate existing ERD diagram against current SQLModel definitions.

### Usage
```bash
python -m backend.scripts.generate_erd --validate
```

### Input Requirements
- Existing ERD documentation file
- Current SQLModel definitions
- Python environment with required dependencies

### Output Specification
- Validation report to stdout
- Exit code: 0 for valid, non-zero for invalid

### Error Conditions
- Missing ERD file → Exit code 1
- Invalid ERD syntax → Exit code 2
- Mismatch with models → Exit code 3

### Success Criteria
- ERD syntax valid
- ERD matches current model definitions
- All entities and relationships correctly represented
