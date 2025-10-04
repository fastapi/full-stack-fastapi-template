"""
Contract tests for CLI interface based on cli-interface.md contract.
These tests MUST fail initially and will pass once CLI implementation is complete.
"""

import subprocess
import sys
from pathlib import Path


class TestCLIInterface:
    """Test CLI interface contract compliance."""

    def test_generate_erd_command_exists(self):
        """Test that generate-erd command is available."""
        # This should fail until CLI is implemented
        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py", "--help"],
            capture_output=True,
            text=True,
        )

        # Should return help text, not error
        assert result.returncode == 0
        assert "Generate Mermaid ERD diagrams" in result.stdout
        assert "--models-path" in result.stdout
        assert "--output-path" in result.stdout
        assert "--validate" in result.stdout
        assert "--verbose" in result.stdout

    def test_generate_erd_default_behavior(self):
        """Test default ERD generation without options."""
        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py"],
            capture_output=True,
            text=True,
        )

        # Should succeed with default paths
        assert result.returncode == 0
        assert "ERD generation CLI not yet implemented" not in result.stdout

    def test_generate_erd_custom_paths(self):
        """Test ERD generation with custom model and output paths."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/generate_erd.py",
                "--models-path",
                "app/models.py",
                "--output-path",
                "../docs/database/erd.mmd",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_generate_erd_validate_flag(self):
        """Test ERD generation with validation flag."""
        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py", "--validate"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_generate_erd_verbose_flag(self):
        """Test ERD generation with verbose flag."""
        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py", "--verbose"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_cli_exit_codes(self):
        """Test CLI exit codes according to contract."""
        # Test successful generation
        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Test invalid models file (should return exit code 2)
        result = subprocess.run(
            [
                sys.executable,
                "scripts/generate_erd.py",
                "--models-path",
                "nonexistent.py",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2

        # Test unwritable output path (should return exit code 3)
        result = subprocess.run(
            [
                sys.executable,
                "scripts/generate_erd.py",
                "--output-path",
                "/nonexistent/path/erd.mmd",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 3

    def test_validate_erd_command(self):
        """Test validate-erd command functionality."""
        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py", "--validate"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should produce validation report
        assert "validation" in result.stdout.lower() or result.returncode != 0

    def test_error_messages_to_stderr(self):
        """Test that error messages are written to stderr."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/generate_erd.py",
                "--models-path",
                "invalid_file.py",
            ],
            capture_output=True,
            text=True,
        )

        # Error messages should go to stderr
        if result.returncode != 0:
            assert result.stderr  # Should have error message
            assert "invalid_file.py" in result.stderr or result.returncode == 2

    def test_output_file_creation(self):
        """Test that ERD output file is created."""
        output_file = Path("../docs/database/erd.mmd")

        # Clean up any existing file
        if output_file.exists():
            output_file.unlink()

        result = subprocess.run(
            [sys.executable, "scripts/generate_erd.py"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_file.exists()

        # File should contain Mermaid ERD syntax
        content = output_file.read_text()
        assert "erDiagram" in content or "mermaid" in content.lower()
