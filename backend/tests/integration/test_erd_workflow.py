"""
Integration tests for ERD generation workflow.
These tests MUST fail initially and will pass once ERD generation is implemented.
"""

import os
import tempfile
from pathlib import Path

import pytest


class TestERDGenerationWorkflow:
    """Test complete ERD generation workflow integration."""

    def test_end_to_end_erd_generation(self):
        """Test complete end-to-end ERD generation from models to documentation."""
        from erd import ERDGenerator

        generator = ERDGenerator()

        # Test with existing models.py
        models_path = Path("app/models.py")
        assert models_path.exists(), "models.py file should exist"

        # Generate ERD
        result = generator.generate_erd()
        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain Mermaid ERD syntax
        assert "erDiagram" in result

        # Should contain entities from models.py
        assert "USER" in result.upper() or "User" in result
        assert "ITEM" in result.upper() or "Item" in result

    def test_model_discovery_integration(self):
        """Test integration between ERD generator and model discovery."""
        from erd import ERDGenerator
        from erd import ModelDiscovery

        # Test model discovery
        discovery = ModelDiscovery()
        model_files = discovery.discover_model_files()
        assert len(model_files) > 0

        # Test ERD generation with discovered models
        generator = ERDGenerator()
        result = generator.generate_erd()

        # Should generate ERD based on discovered models
        assert isinstance(result, str)
        assert "erDiagram" in result

    def test_file_output_integration(self):
        """Test that ERD generation writes to correct output file."""
        from erd import ERDGenerator

        # Use temporary file for testing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_output = f.name

        try:
            generator = ERDGenerator(output_path=temp_output)
            result = generator.generate_erd()

            # Should write to file
            assert Path(temp_output).exists()

            # File content should match generated ERD
            file_content = Path(temp_output).read_text()
            assert file_content == result
            assert "erDiagram" in file_content

        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)

    def test_sqlmodel_parsing_integration(self):
        """Test integration with SQLModel parsing and AST analysis."""
        from erd import ERDGenerator
        from erd import ModelDiscovery

        # Test parsing of actual SQLModel definitions
        discovery = ModelDiscovery()
        models = discovery.discover_all_models()

        assert len(models) > 0, "Should discover models from models.py"

        # Test ERD generation incorporates parsed model information
        generator = ERDGenerator()
        result = generator.generate_erd()

        # Should include model information in ERD
        assert "erDiagram" in result

        # Should include fields and relationships from parsed models
        for _file_path, model_list in models.items():
            for model in model_list:
                assert model["name"].upper() in result or model["name"] in result

    def test_relationship_mapping_integration(self):
        """Test integration of relationship mapping in ERD generation."""
        from erd import ERDGenerator

        generator = ERDGenerator()
        result = generator.generate_erd()

        # Should include relationships between entities
        assert "erDiagram" in result

        # Should show foreign key relationships
        # Based on models.py, should have User-Item relationship
        if "USER" in result.upper() and "ITEM" in result.upper():
            # Should show relationship between User and Item
            assert "||--o{" in result or "--" in result

    def test_constraint_representation_integration(self):
        """Test integration of constraint representation in ERD."""
        from erd import ERDGenerator

        generator = ERDGenerator()
        result = generator.generate_erd()

        # Should represent constraints (PK, FK, etc.)
        assert "erDiagram" in result

        # Should show primary keys
        assert "PK" in result or "primary" in result.lower()

        # Should show foreign keys
        assert "FK" in result or "foreign" in result.lower()

    def test_error_handling_integration(self):
        """Test integration of error handling throughout workflow."""
        from erd import ERDGenerator

        generator = ERDGenerator()

        # Test with invalid models path
        invalid_generator = ERDGenerator(models_path="nonexistent.py")

        with pytest.raises((FileNotFoundError, PermissionError, OSError)):
            invalid_generator.generate_erd()

        # Test with valid path should work
        result = generator.generate_erd()
        assert isinstance(result, str)

    def test_performance_integration(self):
        """Test that complete workflow meets performance requirements."""
        import time

        from erd import ERDGenerator

        generator = ERDGenerator()

        # Test performance requirement: <30 seconds for typical schemas
        start_time = time.time()
        result = generator.generate_erd()
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 30.0, f"ERD generation took {duration}s, should be <30s"

        # Should still produce valid result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_validation_integration(self):
        """Test integration with validation system."""
        from erd import ERDGenerator
        from erd import ERDValidator

        generator = ERDGenerator()
        validator = ERDValidator()

        # Generate ERD
        erd_result = generator.generate_erd()

        # Validate generated ERD
        validation_result = validator.validate_all(erd_result)

        # Should pass validation
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

    def test_documentation_format_integration(self):
        """Test that generated ERD is properly formatted for documentation."""
        from erd import ERDGenerator

        generator = ERDGenerator()
        result = generator.generate_erd()

        # Should be properly formatted for Markdown
        assert "```mermaid" in result or "erDiagram" in result

        # Should have proper structure
        lines = result.split("\n")
        assert any("erDiagram" in line for line in lines)

        # Should be readable and well-formatted
        assert len(result.strip()) > 0
        assert not result.startswith(" ")  # Should not have leading whitespace issues
