# Contract: Pre-commit Hook Integration

## Hook: `erd-generation`

### Purpose
Automatically generate and validate ERD diagrams before each commit to ensure documentation stays current.

### Trigger Conditions
- Any changes to SQLModel definition files
- Any changes to ERD generation configuration
- Manual trigger via `pre-commit run erd-generation`

### Input Requirements
- Modified files list from git
- Current SQLModel definitions
- ERD generation configuration
- Python environment with required dependencies

### Processing Logic
1. **File Detection**: Check if any SQLModel files were modified
2. **Model Parsing**: Parse current SQLModel definitions
3. **ERD Generation**: Generate updated ERD diagram
4. **Validation**: Validate generated ERD against models
5. **Documentation Update**: Update ERD documentation file
6. **Git Integration**: Stage updated documentation if changed

### Output Specification
- Updated ERD documentation file
- Validation report to stdout
- Exit code: 0 for success, non-zero for failure

### Error Handling
- **Parse Errors**: Fail commit with clear error message
- **Validation Errors**: Fail commit with validation report
- **Generation Errors**: Fail commit with generation error details
- **File Errors**: Fail commit with file operation error

### Success Criteria
- ERD diagram generated successfully
- Documentation file updated
- All validation checks pass
- Changes staged for commit

### Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: erd-generation
        name: Generate ERD Diagram
        entry: python -m backend.scripts.generate_erd --pre-commit
        language: system
        files: ^backend/app/models\.py$
        pass_filenames: false
        always_run: false
```

### Integration Requirements
- Pre-commit framework installed and configured
- ERD generation script available in PATH
- Write access to documentation directory
- Git repository with proper permissions

### Performance Considerations
- Hook should complete within 30 seconds
- Only run when SQLModel files are modified
- Cache model metadata when possible
- Fail fast on validation errors

### Rollback Behavior
- Failed commits leave repository in clean state
- No partial ERD updates committed
- Clear error messages for debugging
- Manual override available for emergency commits
