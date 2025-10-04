#!/usr/bin/env python3
"""
CLI script for ERD generation.
"""

import argparse
import sys
import time
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from erd import ERDGenerator


def main():
    """Main CLI entry point for ERD generation."""
    parser = argparse.ArgumentParser(description="Generate Mermaid ERD diagrams from SQLModel definitions")
    parser.add_argument("--models-path", default="app/models.py", help="Path to SQLModel definitions")
    parser.add_argument("--output-path", default="../docs/database/erd.mmd", help="Path for generated ERD documentation")
    parser.add_argument("--validate", action="store_true", help="Run validation checks on generated ERD")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing output file")
    parser.add_argument("--backup", action="store_true", help="Create backup of existing ERD file before overwriting")

    args = parser.parse_args()

    try:
        # Enhanced file system operations
        if not _validate_input_path(args.models_path):
            print(f"Invalid models path: {args.models_path}", file=sys.stderr)
            return 2

        if not _prepare_output_path(args.output_path, args.force, args.backup):
            print(f"Failed to prepare output path: {args.output_path}", file=sys.stderr)
            return 3

        # Initialize ERD generator
        generator = ERDGenerator(
            models_path=args.models_path,
            output_path=args.output_path
        )

        if args.verbose:
            print(f"Models path: {args.models_path}")
            print(f"Output path: {args.output_path}")
            print("Starting ERD generation...")

        # Validate models if requested
        if args.validate:
            if args.verbose:
                print("Validating models...")
            validation_result = _validate_models(generator, args.verbose)
            if not validation_result:
                return 2

        # Generate ERD
        mermaid_code = generator.generate_erd()

        if args.verbose:
            print("ERD generation completed successfully")
            print(f"Generated {len(mermaid_code.splitlines())} lines of Mermaid code")
            _print_output_summary(args.output_path)

        return 0

    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        return 2
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"ERD generation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def _validate_input_path(models_path: str) -> bool:
    """Validate that the models path exists and is accessible."""
    path = Path(models_path)

    if not path.exists():
        return False

    if not path.is_file() and not path.is_dir():
        return False

    # Check if it's readable
    try:
        with open(path) as f:
            f.read(1)  # Try to read one character
        return True
    except (PermissionError, UnicodeDecodeError):
        return False


def _prepare_output_path(output_path: str, force: bool, backup: bool) -> bool:
    """Prepare the output path, creating directories and handling existing files."""
    path = Path(output_path)

    # Create parent directories if they don't exist
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return False

    # Handle existing file
    if path.exists():
        if not force:
            print(f"Output file already exists: {output_path}", file=sys.stderr)
            print("Use --force to overwrite or --backup to create a backup", file=sys.stderr)
            return False

        if backup:
            backup_path = path.with_suffix(f"{path.suffix}.backup.{int(time.time())}")
            try:
                path.rename(backup_path)
                print(f"Created backup: {backup_path}")
            except PermissionError:
                print(f"Warning: Could not create backup of {output_path}", file=sys.stderr)

    # Check if we can write to the output location
    try:
        path.touch()
        path.unlink()  # Remove the test file
        return True
    except PermissionError:
        return False


def _validate_models(generator: ERDGenerator, verbose: bool) -> bool:
    """Enhanced model validation with detailed reporting."""
    try:
        is_valid = generator.validate_models()

        if not is_valid:
            if verbose:
                print("Model validation issues found:")
                # This could be enhanced to show specific validation errors
                print("- Check that all models have primary keys")
                print("- Verify field definitions are correct")
                print("- Ensure foreign key references are valid")

        return is_valid
    except Exception as e:
        if verbose:
            print(f"Validation error: {e}")
        return False


def _print_output_summary(output_path: str) -> None:
    """Print summary information about the generated output."""
    path = Path(output_path)

    if path.exists():
        file_size = path.stat().st_size
        print(f"Output file: {output_path}")
        print(f"File size: {file_size} bytes")

        # Try to count lines
        try:
            with open(path) as f:
                line_count = sum(1 for _ in f)
            print(f"Line count: {line_count}")
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
