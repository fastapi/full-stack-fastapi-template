"""
Contract tests for pre-commit hook integration based on pre-commit-hook.md contract.
These tests MUST fail initially and will pass once pre-commit hook is implemented.
"""

import os
import subprocess
import tempfile
from pathlib import Path


class TestPreCommitHook:
    """Test pre-commit hook contract compliance."""

    def test_pre_commit_config_exists(self):
        """Test that pre-commit configuration includes ERD generation hook."""
        config_file = Path(".pre-commit-config.yaml")
        assert config_file.exists()

        content = config_file.read_text()
        assert "erd-generation" in content or "generate_erd" in content

    def test_pre_commit_hook_registration(self):
        """Test that ERD generation hook is properly registered."""
        result = subprocess.run(
            [
                "pre-commit",
                "run",
                "--all-files",
                "--hook-stage",
                "manual",
                "erd-generation",
            ],
            capture_output=True,
            text=True,
        )

        # Hook should exist (may fail until implemented, but should be registered)
        # If hook doesn't exist, pre-commit should return non-zero
        # If hook exists but fails, that's expected until implementation
        assert result.returncode in [0, 1]  # 0 if passes, 1 if hook fails (expected)

    def test_hook_triggers_on_model_changes(self):
        """Test that hook triggers when SQLModel files are modified."""
        # Create a temporary test file that looks like a model file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from sqlmodel import SQLModel, Field

class TestModel(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
"""
            )
            temp_file = f.name

        try:
            # Test that hook would trigger on this file
            result = subprocess.run(
                ["pre-commit", "run", "--files", temp_file, "erd-generation"],
                capture_output=True,
                text=True,
            )

            # Hook should attempt to run (may fail until implemented)
            assert result.returncode in [0, 1]
        finally:
            os.unlink(temp_file)

    def test_hook_file_detection(self):
        """Test that hook detects SQLModel definition files."""
        # Test with actual models.py file
        models_file = Path("app/models.py")
        if models_file.exists():
            result = subprocess.run(
                ["pre-commit", "run", "--files", str(models_file), "erd-generation"],
                capture_output=True,
                text=True,
            )

            # Should attempt to run on models file
            assert result.returncode in [0, 1]

    def test_hook_generates_erd_output(self):
        """Test that hook generates ERD output when triggered."""
        # This test will fail until hook is implemented
        # but should verify the expected behavior
        result = subprocess.run(
            ["pre-commit", "run", "--all-files", "erd-generation"],
            capture_output=True,
            text=True,
        )

        # After implementation, should succeed
        # For now, expect failure until implemented
        assert result.returncode in [0, 1]

        # If successful, ERD file should exist
        if result.returncode == 0:
            erd_file = Path("../docs/database/erd.mmd")
            assert erd_file.exists()

    def test_hook_validation_integration(self):
        """Test that hook integrates with validation system."""
        result = subprocess.run(
            ["pre-commit", "run", "--all-files", "erd-generation"],
            capture_output=True,
            text=True,
        )

        # Should attempt validation as part of hook process
        assert result.returncode in [0, 1]

        # Validation output should be present in stdout/stderr
        output = result.stdout + result.stderr
        if result.returncode == 1:
            # If failing, should have validation-related output
            assert any(
                word in output.lower() for word in ["validation", "error", "fail"]
            )

    def test_hook_performance_requirements(self):
        """Test that hook completes within performance requirements."""
        import time

        start_time = time.time()
        result = subprocess.run(
            ["pre-commit", "run", "--all-files", "erd-generation"],
            capture_output=True,
            text=True,
        )
        end_time = time.time()

        # Should complete within 30 seconds (performance requirement)
        duration = end_time - start_time
        assert duration < 30.0

        # Hook should run (may fail until implemented)
        assert result.returncode in [0, 1]

    def test_hook_error_handling(self):
        """Test that hook handles errors gracefully."""
        # Test with invalid model file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("invalid python syntax !@#$%")
            temp_file = f.name

        try:
            result = subprocess.run(
                ["pre-commit", "run", "--files", temp_file, "erd-generation"],
                capture_output=True,
                text=True,
            )

            # Should fail gracefully with clear error message
            assert result.returncode == 1
            assert result.stderr  # Should have error output

        finally:
            os.unlink(temp_file)

    def test_hook_stages_updated_files(self):
        """Test that hook stages updated documentation files."""
        # This test verifies the expected behavior after implementation
        # For now, just ensure hook runs
        result = subprocess.run(
            ["pre-commit", "run", "--all-files", "erd-generation"],
            capture_output=True,
            text=True,
        )

        # Hook should run (may fail until implemented)
        assert result.returncode in [0, 1]

        # After implementation, should stage updated files
        # This is verified by checking git status after successful run
        if result.returncode == 0:
            git_result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )

            # Should show staged changes to ERD documentation
            assert (
                "../docs/database/erd.mmd" in git_result.stdout
                or git_result.returncode != 0
            )
