"""
Unit tests for ERD Models module.

Tests the data structures used for model metadata, field metadata,
relationship metadata, and constraint metadata.
"""

import pytest
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from erd import (
    FieldMetadata,
    RelationshipMetadata,
    ConstraintMetadata,
    ModelMetadata
)


class TestFieldMetadata:
    """Test FieldMetadata data structure."""

    def test_field_metadata_creation(self):
        """Test FieldMetadata creation with required fields."""
        field = FieldMetadata(
            name="id",
            type_hint="uuid.UUID",
            is_primary_key=True,
            is_foreign_key=False,
            is_nullable=False
        )
        
        assert field.name == "id"
        assert field.type_hint == "uuid.UUID"
        assert field.is_primary_key is True
        assert field.is_foreign_key is False
        assert field.is_nullable is False
        assert field.constraints == []

    def test_field_metadata_with_constraints(self):
        """Test FieldMetadata with constraints."""
        field = FieldMetadata(
            name="email",
            type_hint="str",
            constraints=["unique", "not_null"]
        )
        
        assert field.constraints == ["unique", "not_null"]

    def test_field_metadata_to_dict(self):
        """Test FieldMetadata to_dict conversion."""
        field = FieldMetadata(
            name="title",
            type_hint="str",
            is_primary_key=False,
            is_foreign_key=False,
            is_nullable=True,
            default_value="Untitled"
        )
        
        field_dict = field.to_dict()
        
        assert field_dict["name"] == "title"
        assert field_dict["type_hint"] == "str"
        assert field_dict["is_primary_key"] is False
        assert field_dict["is_foreign_key"] is False
        assert field_dict["is_nullable"] is True
        assert field_dict["default_value"] == "Untitled"

    def test_field_metadata_post_init(self):
        """Test FieldMetadata __post_init__ behavior."""
        field = FieldMetadata(
            name="id",
            type_hint="int"
        )
        
        # Should initialize empty constraints list
        assert field.constraints == []


class TestRelationshipMetadata:
    """Test RelationshipMetadata data structure."""

    def test_relationship_metadata_creation(self):
        """Test RelationshipMetadata creation."""
        rel = RelationshipMetadata(
            field_name="items",
            target_model="Item",
            relationship_type="one-to-many",
            back_populates="owner",
            foreign_key_field=None,
            cascade="delete"
        )
        
        assert rel.field_name == "items"
        assert rel.target_model == "Item"
        assert rel.relationship_type == "one-to-many"
        assert rel.back_populates == "owner"
        assert rel.foreign_key_field is None
        assert rel.cascade == "delete"

    def test_relationship_metadata_minimal(self):
        """Test RelationshipMetadata with minimal fields."""
        rel = RelationshipMetadata(
            field_name="owner",
            target_model="User",
            relationship_type="many-to-one"
        )
        
        assert rel.field_name == "owner"
        assert rel.target_model == "User"
        assert rel.relationship_type == "many-to-one"
        assert rel.back_populates is None
        assert rel.foreign_key_field is None
        assert rel.cascade is None

    def test_relationship_metadata_foreign_key(self):
        """Test RelationshipMetadata with foreign key field."""
        rel = RelationshipMetadata(
            field_name="owner",
            target_model="User",
            relationship_type="many-to-one",
            foreign_key_field="owner_id"
        )
        
        assert rel.foreign_key_field == "owner_id"


class TestConstraintMetadata:
    """Test ConstraintMetadata data structure."""

    def test_constraint_metadata_creation(self):
        """Test ConstraintMetadata creation."""
        constraint = ConstraintMetadata(
            name="pk_user",
            type="primary_key",
            fields=["id"]
        )
        
        assert constraint.name == "pk_user"
        assert constraint.type == "primary_key"
        assert constraint.fields == ["id"]
        assert constraint.target_table is None
        assert constraint.target_fields is None

    def test_constraint_metadata_foreign_key(self):
        """Test ConstraintMetadata for foreign key."""
        constraint = ConstraintMetadata(
            name="fk_item_owner",
            type="foreign_key",
            fields=["owner_id"],
            target_table="user",
            target_fields=["id"]
        )
        
        assert constraint.name == "fk_item_owner"
        assert constraint.type == "foreign_key"
        assert constraint.fields == ["owner_id"]
        assert constraint.target_table == "user"
        assert constraint.target_fields == ["id"]

    def test_constraint_metadata_unique(self):
        """Test ConstraintMetadata for unique constraint."""
        constraint = ConstraintMetadata(
            name="uk_user_email",
            type="unique",
            fields=["email"]
        )
        
        assert constraint.name == "uk_user_email"
        assert constraint.type == "unique"
        assert constraint.fields == ["email"]


class TestModelMetadata:
    """Test ModelMetadata data structure."""

    def test_model_metadata_creation(self):
        """Test ModelMetadata creation."""
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
        
        relationships = [
            RelationshipMetadata(
                field_name="items",
                target_model="Item",
                relationship_type="one-to-many"
            )
        ]
        
        constraints = [
            ConstraintMetadata(
                name="pk_user",
                type="primary_key",
                fields=["id"]
            )
        ]
        
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=relationships,
            constraints=constraints
        )
        
        assert model.class_name == "User"
        assert model.table_name == "USER"
        assert model.file_path == Path("app/models.py")
        assert model.line_number == 10
        assert len(model.fields) == 2
        assert len(model.relationships) == 1
        assert len(model.constraints) == 1
        assert model.imports == []

    def test_model_metadata_post_init_primary_key(self):
        """Test ModelMetadata __post_init__ primary key detection."""
        fields = [
            FieldMetadata(
                name="email",
                type_hint="str"
            ),
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            )
        ]
        
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        # Should auto-detect primary key
        assert model.primary_key == "id"

    def test_model_metadata_post_init_imports(self):
        """Test ModelMetadata __post_init__ imports initialization."""
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=[],
            relationships=[],
            constraints=[]
        )
        
        # Should initialize empty imports list
        assert model.imports == []

    def test_model_metadata_has_foreign_keys(self):
        """Test ModelMetadata has_foreign_keys property."""
        # Model with foreign key fields
        fields_with_fk = [
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            ),
            FieldMetadata(
                name="owner_id",
                type_hint="uuid.UUID",
                is_foreign_key=True
            )
        ]
        
        model_with_fk = ModelMetadata(
            class_name="Item",
            table_name="ITEM",
            file_path=Path("app/models.py"),
            line_number=20,
            fields=fields_with_fk,
            relationships=[],
            constraints=[]
        )
        
        assert model_with_fk.has_foreign_keys is True
        
        # Model without foreign key fields
        fields_without_fk = [
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            ),
            FieldMetadata(
                name="name",
                type_hint="str"
            )
        ]
        
        model_without_fk = ModelMetadata(
            class_name="Category",
            table_name="CATEGORY",
            file_path=Path("app/models.py"),
            line_number=30,
            fields=fields_without_fk,
            relationships=[],
            constraints=[]
        )
        
        assert model_without_fk.has_foreign_keys is False

    def test_model_metadata_foreign_key_fields_property(self):
        """Test ModelMetadata foreign_key_fields property."""
        fields = [
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            ),
            FieldMetadata(
                name="owner_id",
                type_hint="uuid.UUID",
                is_foreign_key=True
            ),
            FieldMetadata(
                name="category_id",
                type_hint="uuid.UUID",
                is_foreign_key=True
            ),
            FieldMetadata(
                name="name",
                type_hint="str"
            )
        ]
        
        model = ModelMetadata(
            class_name="Item",
            table_name="ITEM",
            file_path=Path("app/models.py"),
            line_number=20,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        fk_fields = model.foreign_key_fields
        assert len(fk_fields) == 2
        assert fk_fields[0].name == "owner_id"
        assert fk_fields[1].name == "category_id"

    def test_model_metadata_primary_key_fields_property(self):
        """Test ModelMetadata primary_key_fields property."""
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
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        pk_fields = model.primary_key_fields
        assert len(pk_fields) == 1
        assert pk_fields[0].name == "id"

    def test_model_metadata_relationship_fields_property(self):
        """Test ModelMetadata relationship_fields property."""
        fields = [
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            ),
            FieldMetadata(
                name="items",
                type_hint="list[Item]"
            ),
            FieldMetadata(
                name="owner",
                type_hint="User | None"
            ),
            FieldMetadata(
                name="name",
                type_hint="str"
            )
        ]
        
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        rel_fields = model.relationship_fields
        assert len(rel_fields) == 2
        assert rel_fields[0].name == "items"
        assert rel_fields[1].name == "owner"

    def test_model_metadata_to_dict(self):
        """Test ModelMetadata to_dict conversion."""
        fields = [
            FieldMetadata(
                name="id",
                type_hint="uuid.UUID",
                is_primary_key=True
            )
        ]
        
        model = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[],
            primary_key="id"
        )
        
        model_dict = model.to_dict()
        
        assert model_dict["class_name"] == "User"
        assert model_dict["table_name"] == "USER"
        assert model_dict["primary_key"] == "id"
        assert len(model_dict["fields"]) == 1
        assert model_dict["fields"][0]["name"] == "id"

    def test_model_metadata_get_field_by_name(self):
        """Test ModelMetadata get_field_by_name method."""
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
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        # Test existing field
        field = model.get_field_by_name("email")
        assert field is not None
        assert field.name == "email"
        
        # Test non-existing field
        field = model.get_field_by_name("nonexistent")
        assert field is None

    def test_model_metadata_has_field(self):
        """Test ModelMetadata has_field method."""
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
            file_path=Path("app/models.py"),
            line_number=10,
            fields=fields,
            relationships=[],
            constraints=[]
        )
        
        # Test existing field
        assert model.has_field("email") is True
        assert model.has_field("id") is True
        
        # Test non-existing field
        assert model.has_field("nonexistent") is False
