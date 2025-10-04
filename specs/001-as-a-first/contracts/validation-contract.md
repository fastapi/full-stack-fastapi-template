# Contract: ERD Validation System

## Validation: `erd-accuracy`

### Purpose
Validate that generated ERD diagrams accurately represent current SQLModel definitions.

### Validation Scope
- Entity completeness and accuracy
- Field definitions and types
- Relationship cardinality and constraints
- Primary key definitions
- Foreign key relationships
- Mermaid syntax validity

### Input Requirements
- Current SQLModel definitions
- Generated ERD diagram (Mermaid syntax)
- Validation configuration
- Python environment with required dependencies

### Validation Rules

#### Entity Validation
- All SQLModel classes with `table=True` must be represented in ERD
- Entity names must match table names exactly
- No extra entities in ERD that don't exist in models
- No missing entities in ERD that exist in models

#### Field Validation
- All model fields must be represented in ERD
- Field types must be accurately represented
- Nullable constraints must be correctly shown
- Default values must be preserved
- Field names must match exactly

#### Relationship Validation
- All foreign key relationships must be represented
- Relationship cardinality must be correct
- Foreign key field names must match
- Constraint types (CASCADE, SET NULL) must be preserved
- No orphaned relationships in ERD

#### Syntax Validation
- Mermaid ERD syntax must be valid
- Diagram must be renderable by Mermaid
- No syntax errors or warnings
- Proper formatting and indentation

### Output Specification
- Validation report with detailed results
- Error count and severity levels
- Specific validation failures with line numbers
- Success/failure status
- Exit code: 0 for valid, non-zero for invalid

### Error Severity Levels
- **Critical**: Missing entities, invalid syntax, broken relationships
- **Warning**: Type mismatches, constraint differences
- **Info**: Formatting issues, optimization suggestions

### Validation Modes
- **Strict**: All validations must pass (default)
- **Permissive**: Allow warnings, fail only on critical errors
- **Report**: Generate report without failing validation

### Success Criteria
- All entities correctly represented
- All fields accurately defined
- All relationships properly shown
- Valid Mermaid syntax
- No critical or warning errors

### Failure Handling
- Detailed error messages for each validation failure
- Line number references for syntax errors
- Suggestions for fixing validation issues
- Clear indication of what needs to be corrected

### Performance Requirements
- Validation must complete within 10 seconds
- Memory usage should be reasonable for typical schemas
- No external dependencies for basic validation
- Caching of validation results when possible

### Integration Points
- CLI interface validation mode
- Pre-commit hook validation
- CI/CD pipeline validation
- Manual validation workflow

### Configuration Options
```python
validation_config = {
    "strict_mode": True,
    "check_syntax": True,
    "validate_relationships": True,
    "validate_constraints": True,
    "max_errors": 10,
    "timeout_seconds": 30
}
```
