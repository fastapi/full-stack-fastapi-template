"""
Multi-file model discovery capability for ERD Generator.
This module handles discovery of SQLModel definitions across multiple files.
"""

import ast
from pathlib import Path
from typing import Any


class ModelDiscovery:
    """Handles discovery of SQLModel classes across multiple files."""

    def __init__(self, base_path: str = "app"):
        self.base_path = Path(base_path)
        self.discovered_models: dict[str, Any] = {}
        self.model_files: set[Path] = set()

    def discover_model_files(self, start_path: str = None) -> set[Path]:
        """
        Discover all Python files that may contain SQLModel definitions.

        Args:
            start_path: Starting directory for discovery (defaults to base_path)

        Returns:
            Set of Path objects for Python files containing models
        """
        if start_path:
            search_path = Path(start_path)
            # If start_path is a specific file, use it directly
            if search_path.is_file():
                if self._contains_sqlmodel_import(search_path):
                    return {search_path}
                else:
                    return set()
            # If start_path is a directory, search in it
        else:
            search_path = self.base_path

        model_files = set()

        # Find all Python files in the search path
        for py_file in search_path.rglob("*.py"):
            if self._contains_sqlmodel_import(py_file):
                model_files.add(py_file)

        self.model_files = model_files
        return model_files

    def _contains_sqlmodel_import(self, file_path: Path) -> bool:
        """Check if a Python file contains SQLModel imports."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                return "SQLModel" in content or "sqlmodel" in content.lower()
        except (OSError, UnicodeDecodeError):
            return False

    def extract_model_classes(self, file_path: Path) -> list[dict[str, Any]]:
        """
        Extract SQLModel class definitions from a Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            List of dictionaries containing model class information
        """
        models = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_sqlmodel_class(node):
                        model_info = {
                            "name": node.name,
                            "file_path": str(file_path),
                            "line_number": node.lineno,
                            "bases": [
                                base.id if hasattr(base, "id") else str(base)
                                for base in node.bases
                            ],
                            "table": self._has_table_attribute(node),
                            "fields": self._extract_fields(node),
                            "relationships": self._extract_relationships_from_class(node),
                        }
                        models.append(model_info)

        except (OSError, UnicodeDecodeError, SyntaxError):
            # Log error but continue processing other files
            pass

        return models

    def _is_sqlmodel_class(self, class_node: ast.ClassDef) -> bool:
        """Check if a class is a SQLModel database table class."""
        # Check if it inherits from SQLModel (directly or indirectly)
        has_sqlmodel = False
        has_table_true = False
        
        # Check direct inheritance from SQLModel
        for base in class_node.bases:
            if hasattr(base, "id") and base.id == "SQLModel":
                has_sqlmodel = True
        
        # Also check if any of the base classes might be SQLModel classes
        # (for cases like User(UserBase, table=True) where UserBase inherits from SQLModel)
        for base in class_node.bases:
            if hasattr(base, "id"):
                base_name = base.id
                # Check if this base class might be a SQLModel class
                # This is a simple heuristic - in a real implementation, 
                # we'd need to track the class hierarchy
                if "Base" in base_name or "Model" in base_name:
                    has_sqlmodel = True
        
        # Check for table=True in the class definition keywords
        # This handles cases like: class User(UserBase, table=True):
        for keyword in class_node.keywords:
            if keyword.arg == "table" and isinstance(keyword.value, ast.Constant):
                if keyword.value.value is True:
                    has_table_true = True
        
        # Only return True if it's both a SQLModel AND has table=True
        return has_sqlmodel and has_table_true

    def _extract_relationships_from_class(self, class_node: ast.ClassDef) -> list[dict]:
        """Extract relationship definitions from a SQLModel class."""
        relationships = []
        
        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Check if it's a Relationship() call
                if (isinstance(item.value, ast.Call) and 
                    hasattr(item.value.func, 'id') and 
                    item.value.func.id == 'Relationship'):
                    
                    field_name = item.target.id
                    field_type = ast.unparse(item.annotation) if item.annotation else "Any"
                    
                    # Extract relationship metadata
                    back_populates = None
                    cascade_delete = False
                    
                    for keyword in item.value.keywords:
                        if keyword.arg == "back_populates" and isinstance(keyword.value, ast.Constant):
                            back_populates = keyword.value.value
                        elif keyword.arg == "cascade_delete" and isinstance(keyword.value, ast.Constant):
                            cascade_delete = keyword.value.value
                    
                    # Infer target model from field type
                    target_model = self._infer_target_model_from_type(field_type, back_populates)
                    
                    # Determine relationship type
                    relationship_type = self._determine_relationship_type_from_field_type(field_type)
                    
                    relationships.append({
                        "field_name": field_name,
                        "field_type": field_type,
                        "target_model": target_model,
                        "relationship_type": relationship_type,
                        "back_populates": back_populates,
                        "cascade_delete": cascade_delete,
                    })
        
        return relationships

    def _infer_target_model_from_type(self, field_type: str, back_populates: str | None) -> str:
        """Infer target model name from field type annotation."""
        # Handle list types like list["Item"] or List[Item]
        if "list[" in field_type.lower() or "List[" in field_type:
            # Extract type from list annotation
            if '"' in field_type:
                # Extract double-quoted type name
                start = field_type.find('"') + 1
                end = field_type.find('"', start)
                if end > start:
                    result = field_type[start:end]
                    return result.strip("'\"")
            elif "'" in field_type:
                # Extract single-quoted type name
                start = field_type.find("'") + 1
                end = field_type.find("'", start)
                if end > start:
                    result = field_type[start:end]
                    return result.strip("'\"")
            elif '[' in field_type and ']' in field_type:
                # Extract type from brackets
                start = field_type.find('[') + 1
                end = field_type.find(']', start)
                if end > start:
                    return field_type[start:end].strip()
        
        # Handle union types like User | None
        if "|" in field_type:
            # Extract the non-None type
            types = [t.strip() for t in field_type.split("|")]
            for t in types:
                if t != "None":
                    return t
        
        # Fallback: use back_populates if available
        if back_populates:
            return back_populates.title()
        
        return "Unknown"

    def _determine_relationship_type_from_field_type(self, field_type: str) -> str:
        """Determine relationship type from field type annotation."""
        field_type_lower = field_type.lower()
        
        if "list[" in field_type_lower or "List[" in field_type_lower:
            return "one-to-many"
        elif "| None" in field_type_lower:
            return "many-to-one"
        else:
            # Default to many-to-one for relationship fields (they're usually foreign keys)
            return "many-to-one"

    def _has_table_attribute(self, class_node: ast.ClassDef) -> bool:
        """Check if a class has table=True attribute."""
        for base in class_node.bases:
            if hasattr(base, "keywords"):
                for keyword in base.keywords:
                    if keyword.arg == "table" and isinstance(
                        keyword.value, ast.Constant
                    ):
                        return keyword.value.value is True
        return False

    def _extract_fields(self, class_node: ast.ClassDef) -> list[str]:
        """Extract field names from a class definition."""
        fields = []
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                field_name = node.target.id
                # Skip private fields (starting with _)
                if not field_name.startswith('_'):
                    fields.append(field_name)
        return fields

    def discover_all_models(self) -> dict[str, list[dict[str, Any]]]:
        """
        Discover all SQLModel classes across all discovered files.

        Returns:
            Dictionary mapping file paths to lists of model information
        """
        all_models = {}

        for file_path in self.discover_model_files():
            models = self.extract_model_classes(file_path)
            if models:
                all_models[str(file_path)] = models

        return all_models
