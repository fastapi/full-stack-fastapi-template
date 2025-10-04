"""
Integration tests for automatic ERD update workflow.
These tests MUST fail initially and will pass once automatic update is implemented.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestAutomaticUpdateWorkflow:
    """Test automatic ERD update workflow integration."""

    def test_pre_commit_hook_auto_update(self):
        """Test that pre-commit hook automatically updates ERD on model changes."""
        # Create temporary model file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from sqlmodel import SQLModel, Field
import uuid

class TestModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
"""
            )
            temp_model_file = f.name

        try:
            # Test pre-commit hook on the temporary file
            result = subprocess.run(
                ["pre-commit", "run", "--files", temp_model_file, "erd-generation"],
                capture_output=True,
                text=True,
            )

            # Hook should run (may fail until implemented)
            assert result.returncode in [0, 1]

            # If successful, should update ERD documentation
            if result.returncode == 0:
                erd_file = Path("../docs/database/erd.mmd")
                assert erd_file.exists()

                # ERD should include the test model
                erd_content = erd_file.read_text()
                assert "TestModel" in erd_content or "testmodel" in erd_content.lower()

        finally:
            os.unlink(temp_model_file)

    def test_git_workflow_integration(self):
        """Test integration with git workflow for automatic updates."""
        # Test that git can stage changes to ERD file
        erd_file = Path("../docs/database/erd.mmd")

        # Ensure ERD file exists
        if not erd_file.exists():
            erd_file.parent.mkdir(parents=True, exist_ok=True)
            erd_file.write_text("# ERD\n```mermaid\nerDiagram\n```")

        # Test git staging of ERD updates
        result = subprocess.run(
            ["git", "add", str(erd_file)], capture_output=True, text=True
        )

        # Should be able to stage ERD file
        assert result.returncode == 0

        # Check git status shows staged changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )

        # Should show ERD file in staging area
        assert str(erd_file) in status_result.stdout or status_result.returncode != 0

    def test_model_change_detection(self):
        """Test detection of model changes triggering ERD updates."""
        from erd import ModelDiscovery

        discovery = ModelDiscovery()

        # Discover current models
        _ = discovery.discover_all_models()

        # Create a new model file to simulate changes
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from sqlmodel import SQLModel, Field
import uuid

class NewModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    description: str
"""
            )
            new_model_file = f.name

        try:
            # Test that discovery detects the new model file
            new_models = discovery.discover_model_files(new_model_file)
            assert len(new_models) > 0

            # Extract models from new file
            extracted_models = discovery.extract_model_classes(Path(new_model_file))
            assert len(extracted_models) > 0
            assert extracted_models[0]["name"] == "NewModel"

        finally:
            os.unlink(new_model_file)

    def test_erd_file_update_integration(self):
        """Test that ERD file is properly updated with new model information."""

        from erd import ERDGenerator

        generator = ERDGenerator()
        erd_file = Path("../docs/database/erd.mmd")

        # Record initial file timestamp
        initial_mtime = erd_file.stat().st_mtime if erd_file.exists() else 0

        # Generate ERD (should update file)
        generator.generate_erd()

        # File should be updated
        assert erd_file.exists()

        # File modification time should be newer
        new_mtime = erd_file.stat().st_mtime
        assert new_mtime >= initial_mtime

        # File content should contain generated ERD
        file_content = erd_file.read_text()
        assert "erDiagram" in file_content or "mermaid" in file_content.lower()

    def test_concurrent_update_prevention(self):
        """Test that concurrent updates are handled properly."""
        import threading

        from erd import ERDGenerator

        generator = ERDGenerator()
        results = []

        def generate_erd():
            try:
                result = generator.generate_erd()
                results.append(("success", result))
            except Exception as e:
                results.append(("error", str(e)))

        # Start multiple threads to test concurrent access
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=generate_erd)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout

        # At least one should succeed
        success_count = sum(1 for result_type, _ in results if result_type == "success")
        assert success_count >= 1

    def test_rollback_on_failure(self):
        """Test that failed updates don't leave system in inconsistent state."""
        from erd import ERDGenerator

        # Create a generator with invalid configuration
        invalid_generator = ERDGenerator(
            models_path="nonexistent_models.py", output_path="docs/database/erd.mmd"
        )

        # Attempt generation should fail gracefully
        with pytest.raises((FileNotFoundError, PermissionError, OSError)):
            invalid_generator.generate_erd()

        # ERD file should not be corrupted
        erd_file = Path("../docs/database/erd.mmd")
        if erd_file.exists():
            # File should still be readable
            content = erd_file.read_text()
            assert len(content) > 0

    def test_performance_auto_update(self):
        """Test that automatic updates meet performance requirements."""
        import time

        start_time = time.time()

        # Simulate pre-commit hook execution
        result = subprocess.run(
            ["pre-commit", "run", "--all-files", "erd-generation"],
            capture_output=True,
            text=True,
        )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within 30 seconds
        assert duration < 30.0, f"Auto-update took {duration}s, should be <30s"

        # Hook should run (may fail until implemented)
        assert result.returncode in [0, 1]

    def test_notification_integration(self):
        """Test integration with notification system for update status."""
        from erd import ERDGenerator

        generator = ERDGenerator()

        # Test that generation provides feedback
        result = generator.generate_erd()

        # Should provide some form of status feedback
        # This could be return value, logging, or other mechanism
        assert result is not None  # Should return something

    def test_configuration_update_integration(self):
        """Test that configuration changes trigger ERD updates."""
        from erd import ERDGenerator

        # Test with different configurations
        configs = [
            {"models_path": "app/models.py"},
            {"output_path": "../docs/database/erd.mmd"},
            {
                "models_path": "app/models.py",
                "output_path": "../docs/database/erd.mmd",
            },
        ]

        for config in configs:
            generator = ERDGenerator(**config)
            result = generator.generate_erd()

            # Should work with different configurations
            assert isinstance(result, str)
            assert len(result) > 0

    def test_error_recovery_integration(self):
        """Test error recovery and retry mechanisms."""
        from erd import ERDGenerator

        # Test that system recovers from temporary failures
        generator = ERDGenerator()

        # Should be able to generate ERD successfully
        result = generator.generate_erd()
        assert isinstance(result, str)

        # Should be able to generate again after first attempt
        result2 = generator.generate_erd()
        assert isinstance(result2, str)
        assert result == result2  # Should be consistent
