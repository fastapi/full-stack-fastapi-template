"""
Unit tests for ERD relationship detection and rendering.
"""

import pytest
from pathlib import Path
import tempfile
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from erd import (
    RelationshipDefinition,
    RelationshipManager,
    RelationshipType,
    Cardinality,
    ModelDiscovery,
    RelationshipMetadata,
)


class TestRelationshipDetection:
    """Test relationship detection from SQLModel definitions."""

    def test_parse_relationship_from_source(self):
        """Test parsing Relationship() calls from source code."""
        # Create temporary model file with relationships
        model_content = '''
from sqlmodel import SQLModel, Field, Relationship
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

class Item(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: User | None = Relationship(back_populates="items")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(model_content)
            temp_file = f.name
        
        try:
            discovery = ModelDiscovery()
            relationships = discovery._parse_relationships_from_source(Path(temp_file), "User")
            
            # Should detect the items relationship
            assert len(relationships) >= 1
            
            items_rel = next((r for r in relationships if r.field_name == "items"), None)
            assert items_rel is not None
            assert items_rel.target_model == "Item"
            assert items_rel.back_populates == "owner"
            assert items_rel.cascade_delete is True
            
        finally:
            os.unlink(temp_file)

    def test_relationship_type_detection(self):
        """Test detection of different relationship types."""
        # Test one-to-many relationship
        rel_meta = RelationshipMetadata(
            field_name="items",
            target_model="Item",
            relationship_type="one-to-many",
            back_populates="owner"
        )
        
        relationship = RelationshipDefinition.from_model_relationship(
            rel_meta, 
            {"table_name": "user"}, 
            {"table_name": "item"}
        )
        
        assert relationship.relationship_type == RelationshipType.ONE_TO_MANY
        assert relationship.from_cardinality == Cardinality.ONE
        assert relationship.to_cardinality == Cardinality.ZERO_OR_MORE

    def test_mermaid_relationship_rendering(self):
        """Test Mermaid relationship syntax generation."""
        relationship = RelationshipDefinition(
            from_entity="USER",
            to_entity="ITEM",
            relationship_type=RelationshipType.ONE_TO_MANY,
            from_cardinality=Cardinality.ONE,
            to_cardinality=Cardinality.ZERO_OR_MORE,
            label="items -> owner"
        )
        
        mermaid_syntax = relationship.to_mermaid_relationship()
        expected = 'USER ||--o{ ITEM : items -> owner'
        assert mermaid_syntax == expected

    def test_relationship_manager(self):
        """Test relationship manager functionality."""
        manager = RelationshipManager()
        
        rel1 = RelationshipDefinition(
            from_entity="USER",
            to_entity="ITEM",
            relationship_type=RelationshipType.ONE_TO_MANY,
            from_cardinality=Cardinality.ONE,
            to_cardinality=Cardinality.ZERO_OR_MORE
        )
        
        manager.add_relationship(rel1)
        
        # Test getting relationships for entity
        user_rels = manager.get_relationships_for_entity("USER")
        assert len(user_rels) == 1
        
        item_rels = manager.get_relationships_for_entity("ITEM")
        assert len(item_rels) == 1
        
        # Test outgoing relationships
        outgoing = manager.get_outgoing_relationships("USER")
        assert len(outgoing) == 1
        assert outgoing[0].to_entity == "ITEM"
        
        # Test incoming relationships
        incoming = manager.get_incoming_relationships("ITEM")
        assert len(incoming) == 1
        assert incoming[0].from_entity == "USER"

    def test_bidirectional_relationship_detection(self):
        """Test detection of bidirectional relationships."""
        discovery = ModelDiscovery()
        
        # Mock model classes with bidirectional relationship
        model_classes = [
            {
                "name": "User",
                "relationships": [
                    RelationshipMetadata(
                        field_name="items",
                        target_model="Item",
                        relationship_type="one-to-many",
                        back_populates="owner"
                    )
                ]
            },
            {
                "name": "Item", 
                "relationships": [
                    RelationshipMetadata(
                        field_name="owner",
                        target_model="User",
                        relationship_type="many-to-one",
                        back_populates="items"
                    )
                ]
            }
        ]
        
        all_relationships = discovery._resolve_bidirectional_relationships(model_classes)
        
        # Both relationships should be marked as bidirectional
        user_rel = all_relationships["User"][0]
        item_rel = all_relationships["Item"][0]
        
        assert user_rel.is_bidirectional is True
        assert item_rel.is_bidirectional is True


class TestERDWithRelationships:
    """Test full ERD generation with relationships."""

    def test_erd_generation_with_relationships(self):
        """Test that ERD generation includes relationship lines."""
        from app.erd_generator import ERDGenerator
        
        # Create temporary model file
        model_content = '''
from sqlmodel import SQLModel, Field, Relationship
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    items: list["Item"] = Relationship(back_populates="owner")

class Item(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: User | None = Relationship(back_populates="items")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(model_content)
            temp_file = f.name
        
        try:
            generator = ERDGenerator(models_path=temp_file)
            mermaid_code = generator.generate_erd()
            
            # Should contain relationship line
            assert "USER ||--o{ ITEM" in mermaid_code or "ITEM }o--|| USER" in mermaid_code
            # Should not include relationship fields as regular fields
            assert "string items" not in mermaid_code
            assert "string owner" not in mermaid_code
            
        finally:
            os.unlink(temp_file)

    def test_relationship_field_filtering(self):
        """Test that relationship fields are filtered from entity field lists."""
        from app.erd_generator import ERDGenerator
        
        # Create temporary model file with relationship fields
        model_content = '''
from sqlmodel import SQLModel, Field, Relationship
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    items: list["Item"] = Relationship(back_populates="owner")

class Item(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: User | None = Relationship(back_populates="items")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(model_content)
            temp_file = f.name
        
        try:
            generator = ERDGenerator(models_path=temp_file)
            generator._discover_models()
            generator._extract_model_metadata()
            
            # Check that relationship fields are not in the field lists
            user_metadata = generator.generated_models["User"]
            item_metadata = generator.generated_models["Item"]
            
            user_field_names = [f.name for f in user_metadata.fields]
            item_field_names = [f.name for f in item_metadata.fields]
            
            # Relationship fields should not be in regular field lists
            assert "items" not in user_field_names
            assert "owner" not in item_field_names
            
            # But they should be in relationship lists
            assert len(user_metadata.relationships) >= 1
            assert len(item_metadata.relationships) >= 1
            
        finally:
            os.unlink(temp_file)
