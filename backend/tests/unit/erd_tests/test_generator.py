"""
Unit tests for ERD Generator module.

Tests the core ERD generation functionality including model discovery,
metadata extraction, relationship generation, and Mermaid output.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from erd import ERDGenerator, ModelMetadata, FieldMetadata, RelationshipMetadata, ERDOutput, EntityDefinition, RelationshipDefinition


class TestERDGenerator:
    """Test ERD Generator core functionality."""

    def test_initialization(self):
        """Test ERD Generator initialization with default parameters."""
        generator = ERDGenerator()
        
        assert generator.models_path == "app/models.py"
        assert generator.output_path == "../docs/database/erd.mmd"
        assert generator.generated_models == {}
        assert generator.model_discovery is not None
        assert generator.validator is not None
        assert generator.mermaid_validator is not None

    def test_initialization_custom_paths(self):
        """Test ERD Generator initialization with custom paths."""
        generator = ERDGenerator(
            models_path="custom/models.py",
            output_path="custom/output.mmd"
        )
        
        assert generator.models_path == "custom/models.py"
        assert generator.output_path == "custom/output.mmd"

    @patch('app.erd_generator.ModelDiscovery')
    def test_discover_models(self, mock_discovery):
        """Test model discovery functionality."""
        # Setup mock
        mock_discovery_instance = Mock()
        mock_discovery_instance.discover_models.return_value = {
            "User": Mock(),
            "Item": Mock()
        }
        mock_discovery.return_value = mock_discovery_instance
        
        generator = ERDGenerator()
        generator.model_discovery = mock_discovery_instance
        
        generator._discover_models()
        
        assert len(generator.discovered_models) == 2
        assert "User" in generator.discovered_models
        assert "Item" in generator.discovered_models

    def test_extract_model_metadata(self):
        """Test model metadata extraction."""
        generator = ERDGenerator()
        
        # Mock discovered models
        mock_user_model = Mock()
        mock_user_model.__name__ = "User"
        mock_user_model.__module__ = "app.models"
        
        mock_item_model = Mock()
        mock_item_model.__name__ = "Item"
        mock_item_model.__module__ = "app.models"
        
        generator.discovered_models = {
            "User": mock_user_model,
            "Item": mock_item_model
        }
        
        # Mock model discovery extract_metadata method
        with patch.object(generator.model_discovery, 'extract_metadata') as mock_extract:
            mock_extract.side_effect = [
                ModelMetadata(
                    class_name="User",
                    table_name="USER",
                    file_path=Path("app/models.py"),
                    line_number=10,
                    fields=[],
                    relationships=[],
                    constraints=[]
                ),
                ModelMetadata(
                    class_name="Item", 
                    table_name="ITEM",
                    file_path=Path("app/models.py"),
                    line_number=20,
                    fields=[],
                    relationships=[],
                    constraints=[]
                )
            ]
            
            generator._extract_model_metadata()
            
            assert len(generator.generated_models) == 2
            assert "User" in generator.generated_models
            assert "Item" in generator.generated_models

    def test_generate_entities(self):
        """Test entity generation from model metadata."""
        generator = ERDGenerator()
        
        # Mock generated models
        user_metadata = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=[
                FieldMetadata(
                    name="id",
                    type_hint="uuid.UUID",
                    is_primary_key=True
                ),
                FieldMetadata(
                    name="email",
                    type_hint="str",
                    is_primary_key=False
                )
            ],
            relationships=[],
            constraints=[]
        )
        
        generator.generated_models = {"User": user_metadata}
        
        entities = generator._generate_entities()
        
        assert len(entities) == 1
        assert entities[0].name == "USER"
        assert len(entities[0].fields) == 2
        assert entities[0].fields[0].name == "id"
        assert entities[0].fields[0].is_primary_key is True

    def test_generate_relationships(self):
        """Test relationship generation with bidirectional deduplication."""
        generator = ERDGenerator()
        
        # Create mock models with bidirectional relationship
        user_metadata = ModelMetadata(
            class_name="User",
            table_name="USER",
            file_path=Path("app/models.py"),
            line_number=10,
            fields=[],
            relationships=[
                RelationshipMetadata(
                    field_name="items",
                    target_model="Item",
                    relationship_type="one-to-many",
                    back_populates="owner",
                    foreign_key_field=None,
                    cascade=None
                )
            ],
            constraints=[]
        )
        
        item_metadata = ModelMetadata(
            class_name="Item",
            table_name="ITEM",
            file_path=Path("app/models.py"),
            line_number=20,
            fields=[],
            relationships=[
                RelationshipMetadata(
                    field_name="owner",
                    target_model="User",
                    relationship_type="many-to-one",
                    back_populates="items",
                    foreign_key_field="owner_id",
                    cascade=None
                )
            ],
            constraints=[]
        )
        
        generator.generated_models = {
            "User": user_metadata,
            "Item": item_metadata
        }
        
        relationships = generator._generate_relationships()
        
        # Should only generate one relationship (the one-to-many direction)
        assert len(relationships) == 1
        assert relationships[0].from_entity == "USER"
        assert relationships[0].to_entity == "ITEM"
        assert relationships[0].relationship_type.value == "1:N"

    def test_is_bidirectional_relationship(self):
        """Test bidirectional relationship detection."""
        generator = ERDGenerator()
        
        # Create mock relationship metadata
        user_rel = RelationshipMetadata(
            field_name="items",
            target_model="Item",
            relationship_type="one-to-many",
            back_populates="owner",
            foreign_key_field=None,
            cascade=None
        )
        
        item_rel = RelationshipMetadata(
            field_name="owner",
            target_model="User",
            relationship_type="many-to-one",
            back_populates="items",
            foreign_key_field="owner_id",
            cascade=None
        )
        
        item_model = ModelMetadata(
            class_name="Item",
            table_name="ITEM",
            file_path=Path("app/models.py"),
            line_number=20,
            fields=[],
            relationships=[item_rel],
            constraints=[]
        )
        
        # Test bidirectional detection
        is_bidirectional = generator._is_bidirectional_relationship(user_rel, item_model)
        assert is_bidirectional is True
        
        # Test non-bidirectional relationship
        non_bidirectional_rel = RelationshipMetadata(
            field_name="other_field",
            target_model="OtherModel",
            relationship_type="many-to-one",
            back_populates=None,
            foreign_key_field=None,
            cascade=None
        )
        
        is_bidirectional2 = generator._is_bidirectional_relationship(non_bidirectional_rel, item_model)
        assert is_bidirectional2 is False

    def test_generate_mermaid_code(self):
        """Test Mermaid code generation."""
        generator = ERDGenerator()
        
        # Mock entities
        entities = [
            EntityDefinition(
                name="USER",
                fields=[],
                description="User entity"
            ),
            EntityDefinition(
                name="ITEM",
                fields=[],
                description="Item entity"
            )
        ]
        
        # Mock relationships
        relationships = [
            RelationshipDefinition(
                from_entity="USER",
                to_entity="ITEM",
                relationship_type=None,  # Will be set by the class
                from_cardinality=None,
                to_cardinality=None
            )
        ]
        
        mermaid_code = generator._generate_mermaid_code(entities, relationships)
        
        assert "erDiagram" in mermaid_code
        assert "USER {" in mermaid_code
        assert "ITEM {" in mermaid_code

    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.mkdir')
    def test_write_output(self, mock_mkdir, mock_open):
        """Test ERD output writing to file."""
        generator = ERDGenerator()
        
        # Mock ERD output
        erd_output = ERDOutput(
            mermaid_code="erDiagram\nUSER { id PK }",
            entities=[],
            relationships=[],
            metadata={"generated_at": "2024-01-01T00:00:00"}
        )
        
        generator._write_output(erd_output)
        
        # Verify file operations
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_open.assert_called_once()

    @patch.object(ERDGenerator, '_discover_models')
    @patch.object(ERDGenerator, '_extract_model_metadata')
    @patch.object(ERDGenerator, '_generate_entities')
    @patch.object(ERDGenerator, '_generate_relationships')
    @patch.object(ERDGenerator, '_generate_mermaid_code')
    @patch.object(ERDGenerator, '_write_output')
    def test_generate_erd_success(self, mock_write, mock_mermaid, mock_rel, 
                                 mock_entities, mock_extract, mock_discover):
        """Test successful ERD generation workflow."""
        generator = ERDGenerator()
        
        # Setup mocks
        mock_entities.return_value = []
        mock_rel.return_value = []
        mock_mermaid.return_value = "erDiagram\nUSER { id PK }"
        
        # Mock validator
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.errors = []
        mock_validation_result.warnings = []
        generator.validator.validate_all.return_value = mock_validation_result
        
        # Mock mermaid validator
        mock_mermaid_validation = Mock()
        mock_mermaid_validation.is_valid = True
        mock_mermaid_validation.errors = []
        mock_mermaid_validation.warnings = []
        generator.mermaid_validator.validate_complete.return_value = mock_mermaid_validation
        
        result = generator.generate_erd()
        
        # Verify workflow
        mock_discover.assert_called_once()
        mock_extract.assert_called_once()
        mock_entities.assert_called_once()
        mock_rel.assert_called_once()
        mock_mermaid.assert_called_once()
        mock_write.assert_called_once()
        
        assert result == "erDiagram\nUSER { id PK }"

    @patch.object(ERDGenerator, '_discover_models')
    def test_generate_erd_failure(self, mock_discover):
        """Test ERD generation failure handling."""
        generator = ERDGenerator()
        
        # Mock discovery to raise exception
        mock_discover.side_effect = Exception("Model discovery failed")
        
        with pytest.raises(Exception) as exc_info:
            generator.generate_erd()
        
        assert "ERD generation failed" in str(exc_info.value)
        assert "Model discovery failed" in str(exc_info.value)

    def test_find_target_model(self):
        """Test target model finding for foreign key fields."""
        generator = ERDGenerator()
        
        # Test with _id suffix
        target = generator._find_target_model("owner_id")
        assert target == "Owner"
        
        # Test with user_id suffix
        target = generator._find_target_model("user_id")
        assert target == "User"
        
        # Test without _id suffix
        target = generator._find_target_model("name")
        assert target is None

    def test_is_relationship_field(self):
        """Test relationship field detection."""
        generator = ERDGenerator()
        
        # Test list type (one-to-many)
        field_meta = FieldMetadata(
            name="items",
            type_hint="list[Item]",
            is_foreign_key=False
        )
        assert generator._is_relationship_field(field_meta) is True
        
        # Test union type with None (many-to-one)
        field_meta = FieldMetadata(
            name="owner",
            type_hint="User | None",
            is_foreign_key=False
        )
        assert generator._is_relationship_field(field_meta) is True
        
        # Test regular field
        field_meta = FieldMetadata(
            name="name",
            type_hint="str",
            is_foreign_key=False
        )
        assert generator._is_relationship_field(field_meta) is False
        
        # Test foreign key field
        field_meta = FieldMetadata(
            name="owner_id",
            type_hint="uuid.UUID",
            is_foreign_key=True
        )
        assert generator._is_relationship_field(field_meta) is False
