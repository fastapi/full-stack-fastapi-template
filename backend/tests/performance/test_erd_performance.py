"""
Performance tests for ERD generation.

Tests that ERD generation completes within performance requirements:
- <30 seconds for schemas with up to 20 tables and 100 fields
- Memory usage stays reasonable for large schemas
- Generation time scales appropriately with schema size
"""

import pytest
import time
import tempfile
from pathlib import Path
from unittest.mock import patch

from erd import ERDGenerator, ModelMetadata, FieldMetadata, RelationshipMetadata


class TestERDPerformance:
    """Test ERD generation performance requirements."""

    def test_performance_small_schema(self):
        """Test performance with small schema (2 tables, 10 fields)."""
        generator = ERDGenerator()
        
        start_time = time.time()
        
        # Mock a small schema
        with patch.object(generator, '_discover_models') as mock_discover, \
             patch.object(generator, '_extract_model_metadata') as mock_extract:
            
            # Create small schema
            user_metadata = ModelMetadata(
                class_name="User",
                table_name="USER",
                file_path=Path("test.py"),
                line_number=1,
                fields=[
                    FieldMetadata(name=f"field_{i}", type_hint="str")
                    for i in range(5)
                ],
                relationships=[],
                constraints=[]
            )
            
            item_metadata = ModelMetadata(
                class_name="Item",
                table_name="ITEM",
                file_path=Path("test.py"),
                line_number=10,
                fields=[
                    FieldMetadata(name=f"field_{i}", type_hint="str")
                    for i in range(5)
                ],
                relationships=[],
                constraints=[]
            )
            
            generator.generated_models = {
                "User": user_metadata,
                "Item": item_metadata
            }
            
            # Generate ERD
            result = generator.generate_erd()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Should complete very quickly (under 1 second for small schema)
            assert generation_time < 1.0, f"Small schema took {generation_time:.2f} seconds"
            assert result is not None
            assert "erDiagram" in result

    def test_performance_medium_schema(self):
        """Test performance with medium schema (10 tables, 50 fields)."""
        generator = ERDGenerator()
        
        start_time = time.time()
        
        # Mock a medium schema
        with patch.object(generator, '_discover_models') as mock_discover, \
             patch.object(generator, '_extract_model_metadata') as mock_extract:
            
            # Create medium schema with 10 tables
            generated_models = {}
            for i in range(10):
                table_name = f"TABLE_{i:02d}"
                model_metadata = ModelMetadata(
                    class_name=f"Model{i}",
                    table_name=table_name,
                    file_path=Path("test.py"),
                    line_number=i * 10,
                    fields=[
                        FieldMetadata(
                            name="id",
                            type_hint="uuid.UUID",
                            is_primary_key=True
                        )
                    ] + [
                        FieldMetadata(name=f"field_{j}", type_hint="str")
                        for j in range(4)  # 5 fields per table = 50 total
                    ],
                    relationships=[],
                    constraints=[]
                )
                generated_models[f"Model{i}"] = model_metadata
            
            generator.generated_models = generated_models
            
            # Generate ERD
            result = generator.generate_erd()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Should complete within reasonable time (under 5 seconds for medium schema)
            assert generation_time < 5.0, f"Medium schema took {generation_time:.2f} seconds"
            assert result is not None
            assert "erDiagram" in result
            assert len(generated_models) == 10

    def test_performance_large_schema(self):
        """Test performance with large schema (20 tables, 100 fields)."""
        generator = ERDGenerator()
        
        start_time = time.time()
        
        # Mock a large schema
        with patch.object(generator, '_discover_models') as mock_discover, \
             patch.object(generator, '_extract_model_metadata') as mock_extract:
            
            # Create large schema with 20 tables
            generated_models = {}
            for i in range(20):
                table_name = f"TABLE_{i:02d}"
                model_metadata = ModelMetadata(
                    class_name=f"Model{i}",
                    table_name=table_name,
                    file_path=Path("test.py"),
                    line_number=i * 10,
                    fields=[
                        FieldMetadata(
                            name="id",
                            type_hint="uuid.UUID",
                            is_primary_key=True
                        )
                    ] + [
                        FieldMetadata(name=f"field_{j}", type_hint="str")
                        for j in range(4)  # 5 fields per table = 100 total
                    ],
                    relationships=[],
                    constraints=[]
                )
                generated_models[f"Model{i}"] = model_metadata
            
            generator.generated_models = generated_models
            
            # Generate ERD
            result = generator.generate_erd()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Must complete within 30 seconds (requirement)
            assert generation_time < 30.0, f"Large schema took {generation_time:.2f} seconds (requirement: <30s)"
            assert result is not None
            assert "erDiagram" in result
            assert len(generated_models) == 20

    def test_performance_complex_relationships(self):
        """Test performance with complex relationship schema."""
        generator = ERDGenerator()
        
        start_time = time.time()
        
        # Mock a schema with complex relationships
        with patch.object(generator, '_discover_models') as mock_discover, \
             patch.object(generator, '_extract_model_metadata') as mock_extract:
            
            # Create schema with many relationships
            generated_models = {}
            
            # Create main user table
            user_metadata = ModelMetadata(
                class_name="User",
                table_name="USER",
                file_path=Path("test.py"),
                line_number=1,
                fields=[
                    FieldMetadata(name="id", type_hint="uuid.UUID", is_primary_key=True),
                    FieldMetadata(name="email", type_hint="str"),
                    FieldMetadata(name="name", type_hint="str")
                ],
                relationships=[],
                constraints=[]
            )
            generated_models["User"] = user_metadata
            
            # Create 15 related tables with relationships
            for i in range(15):
                table_name = f"ITEM_{i:02d}"
                model_metadata = ModelMetadata(
                    class_name=f"Item{i}",
                    table_name=table_name,
                    file_path=Path("test.py"),
                    line_number=(i + 1) * 10,
                    fields=[
                        FieldMetadata(name="id", type_hint="uuid.UUID", is_primary_key=True),
                        FieldMetadata(name="title", type_hint="str"),
                        FieldMetadata(name="user_id", type_hint="uuid.UUID", is_foreign_key=True)
                    ],
                    relationships=[
                        RelationshipMetadata(
                            field_name="owner",
                            target_model="User",
                            relationship_type="many-to-one",
                            back_populates=f"items_{i}",
                            foreign_key_field="user_id",
                            cascade=None
                        )
                    ],
                    constraints=[]
                )
                generated_models[f"Item{i}"] = model_metadata
                
                # Add relationship to user
                user_metadata.relationships.append(
                    RelationshipMetadata(
                        field_name=f"items_{i}",
                        target_model=f"Item{i}",
                        relationship_type="one-to-many",
                        back_populates="owner",
                        foreign_key_field=None,
                        cascade=None
                    )
                )
            
            generator.generated_models = generated_models
            
            # Generate ERD
            result = generator.generate_erd()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Should handle complex relationships efficiently
            assert generation_time < 10.0, f"Complex relationships took {generation_time:.2f} seconds"
            assert result is not None
            assert "erDiagram" in result
            assert len(generated_models) == 16  # 1 User + 15 Items

    def test_performance_memory_usage(self):
        """Test memory usage with large schema."""
        import psutil
        import os
        
        generator = ERDGenerator()
        process = psutil.Process(os.getpid())
        
        # Get initial memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock a large schema
        with patch.object(generator, '_discover_models') as mock_discover, \
             patch.object(generator, '_extract_model_metadata') as mock_extract:
            
            # Create large schema with 20 tables
            generated_models = {}
            for i in range(20):
                table_name = f"TABLE_{i:02d}"
                model_metadata = ModelMetadata(
                    class_name=f"Model{i}",
                    table_name=table_name,
                    file_path=Path("test.py"),
                    line_number=i * 10,
                    fields=[
                        FieldMetadata(name="id", type_hint="uuid.UUID", is_primary_key=True)
                    ] + [
                        FieldMetadata(name=f"field_{j}", type_hint="str")
                        for j in range(9)  # 10 fields per table
                    ],
                    relationships=[],
                    constraints=[]
                )
                generated_models[f"Model{i}"] = model_metadata
            
            generator.generated_models = generated_models
            
            # Generate ERD
            result = generator.generate_erd()
            
            # Check memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (under 100MB for large schema)
            assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"
            assert result is not None

    def test_performance_scaling_linear(self):
        """Test that generation time scales approximately linearly with schema size."""
        generator = ERDGenerator()
        
        # Test with different schema sizes
        schema_sizes = [5, 10, 15, 20]
        generation_times = []
        
        for size in schema_sizes:
            with patch.object(generator, '_discover_models') as mock_discover, \
                 patch.object(generator, '_extract_model_metadata') as mock_extract:
                
                # Create schema with specified size
                generated_models = {}
                for i in range(size):
                    table_name = f"TABLE_{i:02d}"
                    model_metadata = ModelMetadata(
                        class_name=f"Model{i}",
                        table_name=table_name,
                        file_path=Path("test.py"),
                        line_number=i * 10,
                        fields=[
                            FieldMetadata(name="id", type_hint="uuid.UUID", is_primary_key=True),
                            FieldMetadata(name="name", type_hint="str")
                        ],
                        relationships=[],
                        constraints=[]
                    )
                    generated_models[f"Model{i}"] = model_metadata
                
                generator.generated_models = generated_models
                
                start_time = time.time()
                result = generator.generate_erd()
                end_time = time.time()
                
                generation_time = end_time - start_time
                generation_times.append(generation_time)
        
        # Check that times are reasonable for all sizes
        for i, time_taken in enumerate(generation_times):
            assert time_taken < 30.0, f"Schema size {schema_sizes[i]} took {time_taken:.2f} seconds"
        
        # Check that scaling is approximately linear (not exponential)
        # Time should not increase dramatically between sizes
        for i in range(1, len(generation_times)):
            ratio = generation_times[i] / generation_times[i-1]
            assert ratio < 3.0, f"Scaling ratio {ratio:.2f} is too high between sizes {schema_sizes[i-1]} and {schema_sizes[i]}"

    def test_performance_file_operations(self):
        """Test performance of file operations during ERD generation."""
        generator = ERDGenerator()
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Set custom output path
            generator.output_path = temp_path
            
            start_time = time.time()
            
            # Mock a medium schema
            with patch.object(generator, '_discover_models') as mock_discover, \
                 patch.object(generator, '_extract_model_metadata') as mock_extract:
                
                # Create schema with 10 tables
                generated_models = {}
                for i in range(10):
                    table_name = f"TABLE_{i:02d}"
                    model_metadata = ModelMetadata(
                        class_name=f"Model{i}",
                        table_name=table_name,
                        file_path=Path("test.py"),
                        line_number=i * 10,
                        fields=[
                            FieldMetadata(name="id", type_hint="uuid.UUID", is_primary_key=True),
                            FieldMetadata(name="name", type_hint="str")
                        ],
                        relationships=[],
                        constraints=[]
                    )
                    generated_models[f"Model{i}"] = model_metadata
                
                generator.generated_models = generated_models
                
                # Generate ERD (includes file operations)
                result = generator.generate_erd()
                
                end_time = time.time()
                generation_time = end_time - start_time
            
            # File operations should not significantly impact performance
            assert generation_time < 5.0, f"File operations took {generation_time:.2f} seconds"
            
            # Verify file was created
            assert Path(temp_path).exists()
            
            # Verify file content
            file_content = Path(temp_path).read_text()
            assert "erDiagram" in file_content
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
