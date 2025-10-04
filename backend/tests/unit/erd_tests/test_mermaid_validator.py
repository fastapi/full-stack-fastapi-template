"""
Unit tests for Mermaid ERD syntax validation.
"""

import pytest
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from erd import MermaidValidator


class TestMermaidValidator:
    """Test Mermaid syntax validation."""

    def test_valid_erd_syntax(self):
        """Test validation of valid ERD syntax."""
        validator = MermaidValidator()
        
        valid_erd = """
erDiagram

USER {
    uuid id PK
    string name
}

ITEM {
    uuid id PK
    string title
    uuid owner_id FK
}

USER ||--}o ITEM : owns
"""
        
        result = validator.validate_erd_structure(valid_erd)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_erdiagram_declaration(self):
        """Test detection of missing erDiagram declaration."""
        validator = MermaidValidator()
        
        invalid_erd = """
USER {
    uuid id PK
}

ITEM {
    uuid id PK
}
"""
        
        result = validator.validate_erd_structure(invalid_erd)
        assert not result.is_valid
        assert any("Missing erDiagram declaration" in error.message for error in result.errors)

    def test_no_entities(self):
        """Test detection of ERD with no entities."""
        validator = MermaidValidator()
        
        invalid_erd = """
erDiagram

USER ||--}o ITEM : owns
"""
        
        result = validator.validate_erd_structure(invalid_erd)
        assert not result.is_valid
        assert any("No entities found" in error.message for error in result.errors)

    def test_invalid_relationship_syntax(self):
        """Test detection of invalid relationship syntax."""
        validator = MermaidValidator()
        
        invalid_erd = """
erDiagram

USER {
    uuid id PK
}

ITEM {
    uuid id PK
}

USER -- ITEM : invalid
"""
        
        result = validator.validate_erd_structure(invalid_erd)
        assert not result.is_valid
        assert any("Invalid relationship syntax" in error.message for error in result.errors)

    def test_unmatched_braces(self):
        """Test detection of unmatched braces."""
        validator = MermaidValidator()
        
        invalid_erd = """
erDiagram

USER {
    uuid id PK
    string name
"""
        
        result = validator.validate_erd_structure(invalid_erd)
        assert not result.is_valid
        assert any("Unmatched braces" in error.message for error in result.errors)

    def test_entity_and_relationship_counting(self):
        """Test accurate counting of entities and relationships."""
        validator = MermaidValidator()
        
        erd = """
erDiagram

USER {
    uuid id PK
    string name
}

ITEM {
    uuid id PK
    string title
}

CATEGORY {
    uuid id PK
    string name
}

USER ||--}o ITEM : owns
ITEM }o--|| CATEGORY : belongs_to
"""
        
        result = validator.validate_erd_structure(erd)
        assert result.is_valid
        
        # Check info messages for counts
        info_messages = [warning.message for warning in result.warnings]
        assert any("3 entities" in msg for msg in info_messages)
        assert any("2 relationships" in msg for msg in info_messages)

    def test_mermaid_cli_availability_check(self):
        """Test Mermaid CLI availability detection."""
        validator = MermaidValidator()
        
        # This test just ensures the method doesn't crash
        # The actual availability depends on the test environment
        cli_available = validator.mermaid_cli_available
        assert isinstance(cli_available, bool)

    def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        validator = MermaidValidator()
        
        valid_erd = """
erDiagram

USER {
    uuid id PK
    string name
}

ITEM {
    uuid id PK
    string title
    uuid owner_id FK
}

USER ||--}o ITEM : owns
"""
        
        result = validator.validate_complete(valid_erd)
        
        # Structure validation should pass
        assert result.is_valid or len(result.errors) == 0
        
        # Should have info about entities and relationships
        info_messages = [warning.message for warning in result.warnings]
        assert any("entities" in msg and "relationships" in msg for msg in info_messages)

    def test_validation_with_comments(self):
        """Test validation with Mermaid comments."""
        validator = MermaidValidator()
        
        erd_with_comments = """
%% Database ERD Diagram
%% Generated: 2024-01-01T00:00:00

erDiagram

USER {
    uuid id PK
    string name
}

ITEM {
    uuid id PK
    string title
}

%% User owns many items
USER ||--}o ITEM : owns
"""
        
        result = validator.validate_erd_structure(erd_with_comments)
        assert result.is_valid
        assert len(result.errors) == 0
