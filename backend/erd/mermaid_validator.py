"""
Mermaid syntax validation for ERD diagrams.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .validation import ValidationResult, ValidationError, ErrorSeverity


class MermaidValidator:
    """Validates Mermaid ERD syntax using the Mermaid CLI."""

    def __init__(self):
        self.mermaid_cli_available = self._check_mermaid_cli()

    def _check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is available."""
        try:
            result = subprocess.run(
                ["mmdc", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def validate_mermaid_syntax(self, mermaid_content: str) -> ValidationResult:
        """Validate Mermaid ERD syntax."""
        result = ValidationResult(is_valid=True)
        
        if not self.mermaid_cli_available:
            result.add_warning(
                ValidationError(
                    message="Mermaid CLI not available - syntax validation skipped",
                    severity=ErrorSeverity.INFO,
                    error_code="MERMAID_CLI_UNAVAILABLE"
                )
            )
            return result
        
        try:
            # Create temporary file with Mermaid content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_content)
                temp_file = f.name
            
            try:
                # Validate syntax using Mermaid CLI
                validation_result = subprocess.run(
                    ["mmdc", "-i", temp_file, "-o", "/dev/null"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if validation_result.returncode != 0:
                    # Parse error output
                    error_lines = validation_result.stderr.split('\n')
                    for line in error_lines:
                        if line.strip() and "error" in line.lower():
                            result.add_error(
                                ValidationError(
                                    message=f"Mermaid syntax error: {line.strip()}",
                                    severity=ErrorSeverity.CRITICAL,
                                    error_code="MERMAID_SYNTAX_ERROR"
                                )
                            )
                else:
                    # Syntax is valid
                    result.add_warning(
                        ValidationError(
                            message="Mermaid syntax validation passed",
                            severity=ErrorSeverity.INFO,
                            error_code="MERMAID_SYNTAX_VALID"
                        )
                    )
                    
            finally:
                # Clean up temporary file
                Path(temp_file).unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            result.add_error(
                ValidationError(
                    message="Mermaid syntax validation timed out",
                    severity=ErrorSeverity.CRITICAL,
                    error_code="MERMAID_TIMEOUT"
                )
            )
        except Exception as e:
            result.add_error(
                ValidationError(
                    message=f"Mermaid syntax validation failed: {str(e)}",
                    severity=ErrorSeverity.CRITICAL,
                    error_code="MERMAID_VALIDATION_ERROR"
                )
            )
        
        return result

    def validate_erd_structure(self, mermaid_content: str) -> ValidationResult:
        """Validate ERD structure and content."""
        result = ValidationResult(is_valid=True)
        
        lines = mermaid_content.split('\n')
        
        # Check for erDiagram declaration
        if not any('erDiagram' in line for line in lines):
            result.add_error(
                ValidationError(
                    message="Missing erDiagram declaration",
                    severity=ErrorSeverity.CRITICAL,
                    error_code="MISSING_ERDIAGRAM"
                )
            )
        
        # Check for entities
        entity_count = 0
        for line in lines:
            if line.strip().endswith('{') and not line.strip().startswith('%'):
                entity_count += 1
        
        if entity_count == 0:
            result.add_error(
                ValidationError(
                    message="No entities found in ERD",
                    severity=ErrorSeverity.CRITICAL,
                    error_code="NO_ENTITIES"
                )
            )
        
        # Check for relationships
        relationship_count = 0
        for line in lines:
            if '--' in line and not line.strip().startswith('%'):
                relationship_count += 1
        
        # Check for common syntax issues
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check for unclosed braces
            if '{' in line and not line.strip().endswith('{'):
                if line.count('{') != line.count('}'):
                    result.add_error(
                        ValidationError(
                            message=f"Unmatched braces on line {line_num}",
                            severity=ErrorSeverity.CRITICAL,
                            line_number=line_num,
                            error_code="UNMATCHED_BRACES"
                        )
                    )
            
            # Check for invalid relationship syntax
            if '--' in line and not line.strip().startswith('%'):
                if not any(symbol in line for symbol in ['||', '|o', '}o', '}|']):
                    result.add_error(
                        ValidationError(
                            message=f"Invalid relationship syntax on line {line_num}",
                            severity=ErrorSeverity.CRITICAL,
                            line_number=line_num,
                            error_code="INVALID_RELATIONSHIP_SYNTAX"
                        )
                    )
        
        # Add summary info
        result.add_warning(
            ValidationError(
                message=f"ERD contains {entity_count} entities and {relationship_count} relationships",
                severity=ErrorSeverity.INFO,
                error_code="ERD_SUMMARY"
            )
        )
        
        return result

    def validate_complete(self, mermaid_content: str) -> ValidationResult:
        """Perform complete Mermaid ERD validation."""
        result = ValidationResult(is_valid=True)
        
        # Structure validation
        structure_result = self.validate_erd_structure(mermaid_content)
        result.errors.extend(structure_result.errors)
        result.warnings.extend(structure_result.warnings)
        if not structure_result.is_valid:
            result.is_valid = False
        
        # Syntax validation (only if structure is valid)
        if structure_result.is_valid:
            syntax_result = self.validate_mermaid_syntax(mermaid_content)
            result.errors.extend(syntax_result.errors)
            result.warnings.extend(syntax_result.warnings)
            if not syntax_result.is_valid:
                result.is_valid = False
        
        return result