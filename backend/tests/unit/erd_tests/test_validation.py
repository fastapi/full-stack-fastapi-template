"""
Unit tests for ERD Validation module.

Tests the validation system for ERD generation including
model validation, ERD validation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from erd import ERDValidator, ValidationResult, ValidationError, ErrorSeverity, ModelMetadata, FieldMetadata, RelationshipMetadata


class TestValidationError:
    """Test ValidationError data structure."""

    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError(
            message="Test error message",
            severity="error",
            line_number=10,
            error_code="ERR001"
        )
        
        assert error.message == "Test error message"
        assert error.severity == "error"
        assert error.line_number == 10
        assert error.error_code == "ERR001"

    def test_validation_error_to_dict(self):
        """Test ValidationError to_dict conversion."""
        error = ValidationError(
            message="Test error",
            severity="error",
            line_number=5,
            error_code="ERR002"
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["message"] == "Test error"
        assert error_dict["severity"] == "error"
        assert error_dict["line_number"] == 5
        assert error_dict["error_code"] == "ERR002"




class TestValidationResult:
    """Test ValidationResult data structure."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult()
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        error = ValidationError(
            message="Test error",
            severity="error",
            line_number=10,
            error_code="ERR001"
        )
        
        result = ValidationResult()
        result.add_error(error)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0] == error

    def test_validation_result_with_warnings(self):
        """Test ValidationResult with warnings."""
        warning = ValidationError(
            message="Test warning",
            severity=ErrorSeverity.WARNING,
            line_number=15,
            error_code="WARN001"
        )
        
        result = ValidationResult()
        result.add_warning(warning)
        
        assert result.is_valid is True  # Warnings don't make result invalid
        assert len(result.warnings) == 1
        assert result.warnings[0] == warning

    def test_validation_result_to_dict(self):
        """Test ValidationResult to_dict conversion."""
        error = ValidationError(
            message="Test error",
            severity="error",
            line_number=10,
            error_code="ERR001"
        )
        
        warning = ValidationError(
            message="Test warning",
            severity=ErrorSeverity.WARNING,
            line_number=15,
            error_code="WARN001"
        )
        
        result = ValidationResult()
        result.add_error(error)
        result.add_warning(warning)
        
        result_dict = result.to_dict()
        
        assert result_dict["is_valid"] is False
        assert len(result_dict["errors"]) == 1
        assert len(result_dict["warnings"]) == 1
        assert result_dict["errors"][0]["message"] == "Test error"
        assert result_dict["warnings"][0]["message"] == "Test warning"


class TestERDValidator:
    """Test ERDValidator functionality."""

    def test_validator_initialization(self):
        """Test ERDValidator initialization."""
        validator = ERDValidator()
        
        assert validator is not None

    def test_validate_model_metadata_success(self):
        """Test successful model metadata validation."""
        validator = ERDValidator()
        
        # Create valid model metadata
        fields = [
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            ),
            FieldMetadata(
                name="email",
                type_hint="str"
            )
        ]
        
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=None,
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        result = validator.validate_model_metadata(model)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_model_metadata_no_primary_key(self):
        """Test model metadata validation without primary key."""
        validator = ERDValidator()
        
        # Create model without primary key
        fields = [
            FieldMetadata(
                name="name",
                type_hint="str"
            )
        ]
        
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=None,
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        result = validator.validate_model_metadata(model)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "primary key" in result.errors[0].message.lower()

    def test_validate_model_metadata_empty_fields(self):
        """Test model metadata validation with empty fields."""
        validator = ERDValidator()
        
        # Create model with no fields
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=None,
            line_number=10,
            fields=[],
            relationships=[],
            constraints=[]
        )
        
        result = validator.validate_model_metadata(model)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "no fields" in result.errors[0].message.lower()

    def test_validate_erd_syntax_success(self):
        """Test successful ERD syntax validation."""
        validator = ERDValidator()
        
        # Valid Mermaid ERD syntax
        erd_syntax = """erDiagram
    USER {
        uuid id PK
        string email
    }
    
    ITEM {
        uuid id PK
        uuid owner_id FK
    }
    
    USER ||--o{ ITEM : owns"""
        
        result = validator.validate_erd_syntax(erd_syntax)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_erd_syntax_missing_erdiagram(self):
        """Test ERD syntax validation with missing erDiagram declaration."""
        validator = ERDValidator()
        
        # Invalid syntax - missing erDiagram
        erd_syntax = """USER {
        uuid id PK
    }"""
        
        result = validator.validate_erd_syntax(erd_syntax)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "erDiagram" in result.errors[0].message

    def test_validate_erd_syntax_no_entities(self):
        """Test ERD syntax validation with no entities."""
        validator = ERDValidator()
        
        # Valid syntax but no entities
        erd_syntax = "erDiagram"
        
        result = validator.validate_erd_syntax(erd_syntax)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "no entities" in result.errors[0].message.lower()

    def test_validate_erd_syntax_invalid_relationship(self):
        """Test ERD syntax validation with invalid relationship syntax."""
        validator = ERDValidator()
        
        # Invalid relationship syntax
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }
    
    USER -- ITEM : invalid"""
        
        result = validator.validate_erd_syntax(erd_syntax)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
        assert any("relationship" in error.message.lower() for error in result.errors)

    def test_validate_erd_syntax_unmatched_braces(self):
        """Test ERD syntax validation with unmatched braces."""
        validator = ERDValidator()
        
        # Unmatched braces
        erd_syntax = """erDiagram
    USER {
        uuid id PK
        string email"""
        
        result = validator.validate_erd_syntax(erd_syntax)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "brace" in result.errors[0].message.lower()

    def test_validate_all_success(self):
        """Test validate_all method with valid ERD."""
        validator = ERDValidator()
        
        # Valid ERD syntax
        erd_syntax = """erDiagram
    USER {
        uuid id PK
        string email
    }"""
        
        result = validator.validate_all(erd_syntax)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_all_with_errors(self):
        """Test validate_all method with invalid ERD."""
        validator = ERDValidator()
        
        # Invalid ERD syntax
        erd_syntax = """USER {
        uuid id PK
    }"""
        
        result = validator.validate_all(erd_syntax)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1

    def test_validate_entities_exist(self):
        """Test validation that entities exist in ERD."""
        validator = ERDValidator()
        
        # ERD with entities
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }
    
    ITEM {
        uuid id PK
    }"""
        
        result = validator.validate_entities_exist(erd_syntax)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_entities_exist_no_entities(self):
        """Test validation when no entities exist."""
        validator = ERDValidator()
        
        # ERD without entities
        erd_syntax = "erDiagram"
        
        result = validator.validate_entities_exist(erd_syntax)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "no entities" in result.errors[0].message.lower()

    def test_validate_relationships_exist(self):
        """Test validation that relationships exist in ERD."""
        validator = ERDValidator()
        
        # ERD with relationships
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }
    
    ITEM {
        uuid id PK
    }
    
    USER ||--o{ ITEM : owns"""
        
        result = validator.validate_relationships_exist(erd_syntax)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_relationships_exist_no_relationships(self):
        """Test validation when no relationships exist."""
        validator = ERDValidator()
        
        # ERD without relationships
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }"""
        
        result = validator.validate_relationships_exist(erd_syntax)
        
        # This should be valid (entities can exist without relationships)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_mermaid_syntax_basic(self):
        """Test basic Mermaid syntax validation."""
        validator = ERDValidator()
        
        # Valid basic syntax
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }"""
        
        result = validator.validate_mermaid_syntax(erd_syntax)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_mermaid_syntax_complex(self):
        """Test complex Mermaid syntax validation."""
        validator = ERDValidator()
        
        # Complex but valid syntax
        erd_syntax = """erDiagram
    USER {
        uuid id PK
        string email UK
        boolean is_active
    }
    
    ITEM {
        uuid id PK
        string title
        uuid owner_id FK
    }
    
    USER ||--o{ ITEM : owns
    USER }o--|| ITEM : created_by"""
        
        result = validator.validate_mermaid_syntax(erd_syntax)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_count_entities_in_erd(self):
        """Test entity counting in ERD."""
        validator = ERDValidator()
        
        # ERD with 2 entities
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }
    
    ITEM {
        uuid id PK
    }"""
        
        count = validator._count_entities_in_erd(erd_syntax)
        assert count == 2

    def test_count_relationships_in_erd(self):
        """Test relationship counting in ERD."""
        validator = ERDValidator()
        
        # ERD with 1 relationship
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }
    
    ITEM {
        uuid id PK
    }
    
    USER ||--o{ ITEM : owns"""
        
        count = validator._count_relationships_in_erd(erd_syntax)
        assert count == 1

    def test_extract_entity_names(self):
        """Test entity name extraction from ERD."""
        validator = ERDValidator()
        
        # ERD with 2 entities
        erd_syntax = """erDiagram
    USER {
        uuid id PK
    }
    
    ITEM {
        uuid id PK
    }"""
        
        entities = validator._extract_entity_names(erd_syntax)
        assert len(entities) == 2
        assert "USER" in entities
        assert "ITEM" in entities
