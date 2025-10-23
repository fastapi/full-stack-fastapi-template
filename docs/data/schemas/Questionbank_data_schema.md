# Question Bank Data Schema Specification

**Version:** 1.0  
**Last Updated:** October 14, 2025  
**Purpose:** Canonical data model for storing approved K-12 math questions with Singapore Primary curriculum alignment

---

## Table of Contents

1. [Overview](#overview)
2. [Core Question Tables](#core-question-tables)
3. [Learning Objectives / Taxonomy](#learning-objectives--taxonomy)
4. [Question-to-Learning-Objective Mappings](#question-to-learning-objective-mappings)
5. [Image Management](#image-management)
6. [Custom Tags](#custom-tags)
7. [Audit and Tracking](#audit-and-tracking)
8. [Type Data JSON Structures](#type-data-json-structures)
9. [Metadata JSON Structure](#metadata-json-structure)
10. [Complete Question Examples](#complete-question-examples)
11. [Indexing Strategy](#indexing-strategy)
12. [Common Query Patterns](#common-query-patterns)
13. [Entity Relationship Diagram](#entity-relationship-diagram)
14. [Data Integrity Rules](#data-integrity-rules)
15. [Storage Estimates](#storage-estimates)

---

## Overview

This schema defines the canonical data model for storing approved questions for worksheet and assessment generation. Key features:

- **Multi-part Question Support:** Questions can be single-part or have multiple sub-parts
- **Curriculum Alignment:** Questions tagged with Singapore Primary Mathematics learning objectives
- **Flexible Type System:** MCQ (single/multi-select) and Short Answer (text/numeric)
- **Image Support:** Images linked to questions with semantic placeholders
- **Learnosity-Compatible Scoring:** Math engine scoring rules (equivLiteral, equivSymbolic, equivValue, stringMatch)
- **Audit Trail:** Complete change history for compliance
- **Extensible Metadata:** Custom fields for additional attributes

---

## Core Question Tables

### Questions Table

Main table storing single-part and multi-part parent questions.

```sql
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  question_text TEXT NOT NULL,
  question_type VARCHAR(20),  -- 'mcq', 'short_answer' (NULL for multi-part)
  difficulty VARCHAR(10) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  marks NUMERIC(5,2) NOT NULL CHECK (marks > 0),
  time_limit_seconds INT CHECK (time_limit_seconds >= 0),
  is_multipart BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Type-specific data (JSON schema validated in application layer)
  type_data JSONB,
  
  -- Flexible metadata
  metadata JSONB,
  
  -- Version control and status
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by VARCHAR(255),
  version INT NOT NULL DEFAULT 1,
  status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
  
  CONSTRAINT check_question_type_data CHECK (
    (is_multipart = FALSE AND question_type IS NOT NULL AND type_data IS NOT NULL) OR
    (is_multipart = TRUE AND question_type IS NULL AND type_data IS NULL)
  )
);

COMMENT ON COLUMN questions.type_data IS 'JSON structure for MCQ: {options, allow_multiple, shuffle_options}. For Short Answer: {acceptable_answers, answer_type, case_sensitive, max_length, match_type}';
COMMENT ON COLUMN questions.metadata IS 'JSON structure: {hint, explanation, custom_fields}';
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Primary key |
| `title` | VARCHAR(200) | Yes | Short descriptive title |
| `question_text` | TEXT | Yes | Full question text (may include image placeholders) |
| `question_type` | VARCHAR(20) | Conditional | 'mcq' or 'short_answer' (NULL for multi-part) |
| `difficulty` | VARCHAR(10) | Yes | 'easy', 'medium', or 'hard' |
| `marks` | NUMERIC(5,2) | Yes | Points awarded (must be > 0) |
| `time_limit_seconds` | INT | No | Suggested time limit |
| `is_multipart` | BOOLEAN | Yes | Whether question has parts |
| `type_data` | JSONB | Conditional | Question-type specific data |
| `metadata` | JSONB | No | Hints, explanations, custom fields |
| `status` | VARCHAR(20) | Yes | 'draft', 'active', or 'archived' |
| `version` | INT | Yes | Version number (for tracking changes) |
| `created_at` | TIMESTAMPTZ | Yes | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Yes | Last update timestamp |
| `created_by` | VARCHAR(255) | No | Creator user ID |

---

### Question Parts Table

Stores parts for multi-part questions only.

```sql
CREATE TABLE question_parts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  part_id VARCHAR(10) NOT NULL,  -- 'a', 'b', 'c' or '1', '2', '3'
  part_sequence INT NOT NULL CHECK (part_sequence > 0),
  part_text TEXT NOT NULL,
  question_type VARCHAR(20) NOT NULL CHECK (question_type IN ('mcq', 'short_answer')),
  marks NUMERIC(5,2) NOT NULL CHECK (marks > 0),
  
  -- Type-specific data (same JSON schemas as questions table)
  type_data JSONB NOT NULL,
  metadata JSONB,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE (question_id, part_id),
  UNIQUE (question_id, part_sequence)
);

COMMENT ON TABLE question_parts IS 'Sub-questions for multi-part questions';
COMMENT ON COLUMN question_parts.part_id IS 'Human-readable label: a, b, c or 1, 2, 3';
COMMENT ON COLUMN question_parts.part_sequence IS 'Numeric ordering within parent question (1, 2, 3...)';
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Primary key |
| `question_id` | UUID | Yes | Foreign key to parent question |
| `part_id` | VARCHAR(10) | Yes | Display label (a, b, c or 1, 2, 3) |
| `part_sequence` | INT | Yes | Ordering sequence (must be > 0) |
| `part_text` | TEXT | Yes | Text of the sub-question |
| `question_type` | VARCHAR(20) | Yes | 'mcq' or 'short_answer' |
| `marks` | NUMERIC(5,2) | Yes | Points for this part |
| `type_data` | JSONB | Yes | Question-type specific data |
| `metadata` | JSONB | No | Hints, explanations for this part |

---

## Learning Objectives / Taxonomy

### Learning Objectives Table

Flattened curriculum hierarchy storing Singapore Primary Mathematics learning objectives.

```sql
CREATE TABLE learning_objectives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) NOT NULL UNIQUE,  -- e.g., 'P4-NA-DEC-1.5'
  subject VARCHAR(50) NOT NULL,  -- 'Mathematics', 'Science', etc.
  grade_level VARCHAR(10) NOT NULL,  -- 'P1', 'P2', ..., 'P6'
  topic VARCHAR(100) NOT NULL,  -- e.g., 'Decimals', 'Fractions'
  topic_number VARCHAR(10),  -- e.g., '1', '2', '3'
  subtopic VARCHAR(100),  -- e.g., 'Rounding', 'Place Value'
  learning_objective TEXT,  -- e.g., 'Addition and Subtraction'
  subtopic_number VARCHAR(10),  -- e.g., '1', '2'
  objective_number VARCHAR(10),  -- e.g., '1.5', '2.3'
  description TEXT NOT NULL,  -- Full description of the learning outcome
  display_order INT NOT NULL,  -- For ordering within curriculum
  
  -- Curriculum versioning
  curriculum_version TEXT NOT NULL DEFAULT 'sg-primary-math-2025',
  effective_from DATE NOT NULL,
  effective_to DATE,  -- NULL if currently active
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE learning_objectives IS 'Singapore Primary Mathematics curriculum learning objectives';
COMMENT ON COLUMN learning_objectives.code IS 'Unique curriculum code: P{grade}-{strand}-{topic}-{subtopic}.{objective}';
COMMENT ON COLUMN learning_objectives.topic_number IS 'Numeric identifier for topic within grade level';
COMMENT ON COLUMN learning_objectives.display_order IS 'Global ordering for curriculum tree display';
COMMENT ON COLUMN learning_objectives.curriculum_version IS 'Version identifier for curriculum (e.g., sg-primary-math-2025)';
```

**Example Records:**

```sql
INSERT INTO learning_objectives (
  code, subject, grade_level, topic, topic_number, subtopic, 
  learning_objective, subtopic_number, objective_number, 
  description, display_order, curriculum_version, effective_from
) VALUES
(
  'P4-NA-DEC-1.5', 'Mathematics', 'P4', 'Decimals', '3', 'Rounding', 
  'Rounding Decimals', '1', '5', 
  'Round decimals to 1 decimal place', 145, 'sg-primary-math-2025', '2025-01-01'
),
(
  'P4-NA-F-2.3', 'Mathematics', 'P4', 'Fractions', '2', 'Operations', 
  'Adding Fractions', '2', '3', 
  'Add fractions with unlike denominators', 167, 'sg-primary-math-2025', '2025-01-01'
),
(
  'P3-M-L-1.2', 'Mathematics', 'P3', 'Measurement', '4', 'Length', 
  'Converting Units', '1', '2', 
  'Convert between m, cm, and mm', 89, 'sg-primary-math-2025', '2025-01-01'
);
```

---

## Question-to-Learning-Objective Mappings

### Question Learning Objectives

Many-to-many junction table linking questions to learning objectives (multi-label support).

```sql
CREATE TABLE question_learning_objectives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  learning_objective_id UUID NOT NULL REFERENCES learning_objectives(id) ON DELETE CASCADE,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE (question_id, learning_objective_id)
);

COMMENT ON TABLE question_learning_objectives IS 'Many-to-many: Questions can have multiple learning objectives';
COMMENT ON COLUMN question_learning_objectives.is_primary IS 'Exactly one tag should be marked primary for reporting';
```

---

### Question Part Learning Objectives

Many-to-many junction table linking question parts to learning objectives.

```sql
CREATE TABLE question_part_learning_objectives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_part_id UUID NOT NULL REFERENCES question_parts(id) ON DELETE CASCADE,
  learning_objective_id UUID NOT NULL REFERENCES learning_objectives(id) ON DELETE CASCADE,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE (question_part_id, learning_objective_id)
);

COMMENT ON TABLE question_part_learning_objectives IS 'Many-to-many: Question parts can have multiple learning objectives';
```

---

## Image Management

### Images Table

Stores image assets with metadata (images stored in object storage, not DB).

```sql
CREATE TABLE images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_path TEXT NOT NULL,  -- Relative path or URL
  file_name VARCHAR(255) NOT NULL,
  file_size BIGINT NOT NULL,
  mime_type VARCHAR(50) NOT NULL,
  width INT,
  height INT,
  alt_text TEXT,
  caption TEXT,
  storage_type VARCHAR(20) NOT NULL CHECK (storage_type IN ('local', 's3', 'cdn', 'url')),
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by VARCHAR(255)
);

COMMENT ON TABLE images IS 'Image assets stored in object storage (S3/GCS/CDN)';
COMMENT ON COLUMN images.file_path IS 'Full path: s3://bucket/questions/2025/10/img_abc123.png OR https://cdn.example.com/img_abc123.png';
COMMENT ON COLUMN images.storage_type IS 'Where the image is stored: local filesystem, S3, CDN, or external URL';
```

---

### Question Images

Junction table linking images to questions or question parts.

```sql
CREATE TABLE question_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
  question_part_id UUID REFERENCES question_parts(id) ON DELETE CASCADE,
  placeholder_ref VARCHAR(50),  -- Internal reference (e.g., 'triangle', 'diagram_a')
  position VARCHAR(20) NOT NULL DEFAULT 'before_text' CHECK (position IN ('before_text', 'after_text', 'option')),
  display_order INT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  CHECK (
    (question_id IS NOT NULL AND question_part_id IS NULL) OR
    (question_id IS NULL AND question_part_id IS NOT NULL)
  )
);

COMMENT ON TABLE question_images IS 'Links images to questions or parts using simple block-level positioning';
COMMENT ON COLUMN question_images.placeholder_ref IS 'Optional internal reference name for tracking (e.g., "triangle_diagram", "bar_chart")';
COMMENT ON COLUMN question_images.position IS 'Where image displays: before_text (above question), after_text (below question), or option (as MCQ choice)';
COMMENT ON COLUMN question_images.display_order IS 'Order of images when multiple images share the same position';
```

---

## Custom Tags

### Custom Tags Table

Flexible tagging system for non-curriculum tags (skills, contexts, themes).

```sql
CREATE TABLE custom_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_name VARCHAR(100) NOT NULL,
  tag_category VARCHAR(50),  -- e.g., 'skill', 'context', 'real_world_application'
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE (tag_name, tag_category)
);

COMMENT ON TABLE custom_tags IS 'Flexible tagging system for non-curriculum tags (skills, contexts, themes)';
COMMENT ON COLUMN custom_tags.tag_category IS 'Groups tags into categories: skill (problem-solving), context (real-world), theme (money)';
```

**Example Records:**

```sql
INSERT INTO custom_tags (tag_name, tag_category) VALUES
('problem-solving', 'skill'),
('estimation', 'skill'),
('real-world', 'context'),
('money', 'theme'),
('measurement', 'theme'),
('visual-spatial', 'skill');
```

---

### Question Tags

Many-to-many junction table for custom tags.

```sql
CREATE TABLE question_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES custom_tags(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE (question_id, tag_id)
);

COMMENT ON TABLE question_tags IS 'Many-to-many: Questions can have multiple custom tags';
```

---

## Audit and Tracking

### Audit Log Table

Immutable audit trail for all changes (7-year retention for compliance).

```sql
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  entity_type VARCHAR(50) NOT NULL,  -- 'question', 'question_part', 'tag', 'learning_objective'
  entity_id UUID NOT NULL,
  action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'approve', 'delete', 'archive')),
  changes JSONB NOT NULL,  -- JSON diff of changes
  user_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_log IS 'Append-only audit log for compliance and change tracking (7-year retention)';
COMMENT ON COLUMN audit_log.changes IS 'JSON diff showing before/after values: {"field": {"old": "...", "new": "..."}}';
```

**Example Audit Log Entry:**

```json
{
  "entity_type": "question",
  "entity_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "update",
  "changes": {
    "difficulty": {"old": "easy", "new": "medium"},
    "marks": {"old": 1.0, "new": 2.0},
    "metadata.explanation": {"old": null, "new": "Detailed solution added"}
  },
  "user_id": "reviewer@example.com",
  "created_at": "2025-10-14T10:30:00Z"
}
```

---

## Type Data JSON Structures

### MCQ Type Data

**Schema:**
```json
{
  "options": [
    {
      "id": "a",
      "text": "Option text here",
      "is_correct": false
    }
  ],
  "allow_multiple": false,
  "shuffle_options": false
}
```

**Field Definitions:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `options` | Array | Yes | 2-6 items | Array of option objects |
| `options[].id` | String | Yes | Pattern: `^[a-z]$` | Option label: a, b, c, d, e, f |
| `options[].text` | String | Yes | 1-500 chars | Option display text |
| `options[].is_correct` | Boolean | Yes | - | Whether this option is correct |
| `allow_multiple` | Boolean | No (default: false) | - | If true, allows multiple correct selections |
| `shuffle_options` | Boolean | No (default: false) | - | If true, randomize option order on display |

**Validation Rules:**
- Single-select (`allow_multiple=false`): Exactly 1 option must have `is_correct=true`
- Multi-select (`allow_multiple=true`): At least 1 option must have `is_correct=true`
- No duplicate option text (case-insensitive comparison)
- Option IDs must be sequential: a, b, c, d (no gaps)

**Example 1: Single-Select MCQ**
```json
{
  "options": [
    {"id": "a", "text": "3.4", "is_correct": false},
    {"id": "b", "text": "3.5", "is_correct": true},
    {"id": "c", "text": "3.6", "is_correct": false},
    {"id": "d", "text": "4.0", "is_correct": false}
  ],
  "allow_multiple": false,
  "shuffle_options": true
}
```

**Example 2: Multi-Select MCQ**
```json
{
  "options": [
    {"id": "a", "text": "Circle", "is_correct": false},
    {"id": "b", "text": "Square", "is_correct": true},
    {"id": "c", "text": "Rectangle", "is_correct": true},
    {"id": "d", "text": "Triangle", "is_correct": false}
  ],
  "allow_multiple": true,
  "shuffle_options": false
}
```

**Example 3: True/False (Special MCQ)**
```json
{
  "options": [
    {"id": "a", "text": "True", "is_correct": false},
    {"id": "b", "text": "False", "is_correct": true}
  ],
  "allow_multiple": false,
  "shuffle_options": false
}
```

---

### Short Answer Type Data

**Schema:**
```json
{
  "acceptable_answers": ["answer1", "answer2"],
  "answer_type": "text",
  "case_sensitive": false,
  "max_length": 250,
  "match_type": "equivLiteral"
}
```

**Field Definitions:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `acceptable_answers` | Array | Yes | 1-10 items | List of acceptable answer strings |
| `answer_type` | String | Yes | 'text' or 'numeric' | Type of answer expected |
| `case_sensitive` | Boolean | No (default: false) | - | Whether to match case exactly |
| `max_length` | Integer | No (default: 250) | 1-250 | Maximum characters allowed |
| `match_type` | String | No (default: 'equivLiteral') | See below | Learnosity-style matching rule |

**Match Type Options (Learnosity Scoring Rules):**

| Match Type | Description | Use Case | Example |
|------------|-------------|----------|---------|
| `equivLiteral` | Exact string match (after trimming/case normalization) | Simple text answers | "rectangle" matches "rectangle" |
| `equivSymbolic` | Symbolic mathematical equivalence | Algebraic expressions | "2x + 3" matches "3 + 2x" |
| `equivValue` | Numerical value equivalence | Numeric answers with rounding | "3.5" matches "3.50" or "7/2" |
| `stringMatch` | Substring or pattern matching | Free-form text with flexible matching | "the answer is 5" matches if contains "5" |

**Reference:** [Learnosity Math Engine Scoring Guide](https://authorguide.learnosity.com/hc/en-us/categories/360000076638-Scoring-with-Math-Engine)

**Validation Rules:**
- At least 1 acceptable answer required
- All answers trimmed of leading/trailing whitespace
- For `answer_type=numeric` with `match_type=equivValue`, answers should be numeric strings
- For `answer_type=text`, `match_type` typically `equivLiteral` or `stringMatch`

**Example 1: Text Answer with Exact Match**
```json
{
  "acceptable_answers": ["rectangle"],
  "answer_type": "text",
  "case_sensitive": false,
  "max_length": 50,
  "match_type": "equivLiteral"
}
```

**Example 2: Text Answer with Multiple Acceptable Forms**
```json
{
  "acceptable_answers": ["3/8", "three eighths", "0.375"],
  "answer_type": "text",
  "case_sensitive": false,
  "max_length": 100,
  "match_type": "equivLiteral"
}
```

**Example 3: Numeric Answer with Value Equivalence**
```json
{
  "acceptable_answers": ["3.5", "3.50", "7/2"],
  "answer_type": "numeric",
  "case_sensitive": false,
  "max_length": 20,
  "match_type": "equivValue"
}
```

**Example 4: Numeric Answer with Unit (Text Match)**
```json
{
  "acceptable_answers": ["5 cm", "5cm", "50 mm", "50mm"],
  "answer_type": "text",
  "case_sensitive": false,
  "max_length": 50,
  "match_type": "equivLiteral"
}
```

**Example 5: Algebraic Expression (Symbolic Equivalence)**
```json
{
  "acceptable_answers": ["2x + 3", "3 + 2x", "x + x + 3"],
  "answer_type": "text",
  "case_sensitive": false,
  "max_length": 100,
  "match_type": "equivSymbolic"
}
```

**Example 6: Flexible Text Match (Substring)**
```json
{
  "acceptable_answers": ["perimeter"],
  "answer_type": "text",
  "case_sensitive": false,
  "max_length": 250,
  "match_type": "stringMatch"
}
```

---

## Metadata JSON Structure

**Schema:**
```json
{
  "hint": "string",
  "explanation": "string",
  "custom_fields": {
    "key": "value"
  }
}
```

**Field Definitions:**

| Field | Type | Required | Max Length | Description |
|-------|------|----------|------------|-------------|
| `hint` | String | No | 1000 chars | Hint provided to learner before revealing answer |
| `explanation` | String | No | Unlimited | Worked solution or explanation shown after answer |
| `custom_fields` | Object | No | - | Extensible key-value pairs for future metadata |

**Example 1: Simple Metadata (Hint + Explanation)**
```json
{
  "hint": "Look at the digit in the hundredths place. If it's 5 or more, round up.",
  "explanation": "The number 3.456 has 5 in the hundredths place. Since 5 ≥ 5, we round the tenths place up from 4 to 5, giving us 3.5."
}
```

**Example 2: Explanation Only**
```json
{
  "explanation": "Step 1: Draw 8 equal slices.\nStep 2: Shade 3 slices.\nStep 3: Count remaining slices: 8 - 3 = 5.\nStep 4: Write as fraction: 5/8."
}
```

**Example 3: Rich Metadata with Custom Fields**
```json
{
  "hint": "Draw a diagram to visualize the problem.",
  "explanation": "You ate 3 out of 8 total slices, so the fraction is 3/8. To find what's left: 8/8 - 3/8 = 5/8.",
  "custom_fields": {
    "difficulty_rating_teacher": 3.2,
    "prerequisite_skills": ["fraction_basics", "subtraction"],
    "common_misconceptions": ["Students may subtract numerators and denominators separately"],
    "time_estimate_minutes": 3,
    "bloom_taxonomy_level": "apply",
    "cognitive_demand": "medium"
  }
}
```

**Example 4: Minimal Metadata**
```json
{
  "explanation": "Round to the nearest tenth. The digit in the hundredths place is 5, so round up."
}
```

**Example 5: No Metadata (All Optional)**
```json
{}
```

---

## Complete Question Examples

### Example 1: Single-Part MCQ

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Rounding Decimals to 1 d.p.",
  "question_text": "Round 3.456 to 1 decimal place.",
  "question_type": "mcq",
  "difficulty": "easy",
  "marks": 1.0,
  "time_limit_seconds": 60,
  "is_multipart": false,
  "type_data": {
    "options": [
      {"id": "a", "text": "3.4", "is_correct": false},
      {"id": "b", "text": "3.5", "is_correct": true},
      {"id": "c", "text": "3.6", "is_correct": false},
      {"id": "d", "text": "4.0", "is_correct": false}
    ],
    "allow_multiple": false,
    "shuffle_options": true
  },
  "metadata": {
    "hint": "Look at the digit in the hundredths place.",
    "explanation": "The number 3.456 has 5 in the hundredths place. Since 5 ≥ 5, round up: 3.5."
  },
  "status": "active",
  "version": 1,
  "created_at": "2025-10-13T14:30:00Z",
  "updated_at": "2025-10-13T14:30:00Z",
  "created_by": "reviewer@example.com"
}
```

---

### Example 2: Single-Part Short Answer (Numeric with equivValue)

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Converting Fractions to Decimals",
  "question_text": "Convert the fraction 3/4 to a decimal.",
  "question_type": "short_answer",
  "difficulty": "medium",
  "marks": 2.0,
  "time_limit_seconds": 120,
  "is_multipart": false,
  "type_data": {
    "acceptable_answers": ["0.75", "0.750", ".75", "3/4"],
    "answer_type": "numeric",
    "case_sensitive": false,
    "max_length": 20,
    "match_type": "equivValue"
  },
  "metadata": {
    "hint": "Divide the numerator by the denominator.",
    "explanation": "3 ÷ 4 = 0.75. You can also think of it as 75/100 or 75 hundredths."
  },
  "status": "active",
  "version": 1,
  "created_at": "2025-10-13T15:00:00Z",
  "updated_at": "2025-10-13T15:00:00Z",
  "created_by": "reviewer@example.com"
}
```

---

### Example 3: Multi-Part Question with Parts

**Parent Question:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "title": "Fraction Pizza Problem",
  "question_text": "Look at the pizza divided into 8 equal slices shown above.",
  "question_type": null,
  "difficulty": "medium",
  "marks": 3.0,
  "time_limit_seconds": 300,
  "is_multipart": true,
  "type_data": null,
  "metadata": {},
  "status": "active",
  "version": 1,
  "created_at": "2025-10-13T16:00:00Z",
  "updated_at": "2025-10-13T16:00:00Z",
  "created_by": "reviewer@example.com"
}
```

**Part A:**
```json
{
  "id": "771e8400-e29b-41d4-a716-446655440003",
  "question_id": "770e8400-e29b-41d4-a716-446655440002",
  "part_id": "a",
  "part_sequence": 1,
  "part_text": "If you eat 3 slices, what fraction of the pizza did you eat?",
  "question_type": "short_answer",
  "marks": 1.5,
  "type_data": {
    "acceptable_answers": ["3/8", "0.375"],
    "answer_type": "text",
    "case_sensitive": false,
    "max_length": 50,
    "match_type": "equivLiteral"
  },
  "metadata": {
    "explanation": "You ate 3 out of 8 total slices, so the fraction is 3/8."
  },
  "created_at": "2025-10-13T16:00:00Z"
}
```

**Part B:**
```json
{
  "id": "772e8400-e29b-41d4-a716-446655440004",
  "question_id": "770e8400-e29b-41d4-a716-446655440002",
  "part_id": "b",
  "part_sequence": 2,
  "part_text": "What fraction of the pizza is left?",
  "question_type": "short_answer",
  "marks": 1.5,
  "type_data": {
    "acceptable_answers": ["5/8", "0.625"],
    "answer_type": "text",
    "case_sensitive": false,
    "max_length": 50,
    "match_type": "equivLiteral"
  },
  "metadata": {
    "hint": "Subtract the fraction you ate from the whole pizza (8/8).",
    "explanation": "8/8 - 3/8 = 5/8. Five slices remain out of 8 total."
  },
  "created_at": "2025-10-13T16:00:00Z"
}
```

**Associated Image:**
```json
{
  "image": {
    "id": "880e8400-e29b-41d4-a716-446655440005",
    "file_path": "s3://questionbank-images/2025/10/pizza_8slices_abc123.png",
    "file_name": "pizza_8slices.png",
    "file_size": 145820,
    "mime_type": "image/png",
    "width": 800,
    "height": 800,
    "alt_text": "Pizza divided into 8 equal slices",
    "caption": null,
    "storage_type": "s3",
    "created_at": "2025-10-13T16:00:00Z"
  },
  "question_image_link": {
    "id": "881e8400-e29b-41d4-a716-446655440006",
    "image_id": "880e8400-e29b-41d4-a716-446655440005",
    "question_id": "770e8400-e29b-41d4-a716-446655440002",
    "question_part_id": null,
    "placeholder_ref": "pizza_diagram",
    "position": "before_text",
    "display_order": 1,
    "created_at": "2025-10-13T16:00:00Z"
  }
}
```

**Rendered Output:**
```
[IMAGE: Pizza divided into 8 equal slices]

Look at the pizza divided into 8 equal slices shown above.

(a) If you eat 3 slices, what fraction of the pizza did you eat?

(b) What fraction of the pizza is left?
```

**Learning Objective Mappings:**
```json
[
  {
    "question_part_id": "771e8400-e29b-41d4-a716-446655440003",
    "learning_objective_id": "LO-UUID-P3-F-1.1",
    "is_primary": true
  },
  {
    "question_part_id": "772e8400-e29b-41d4-a716-446655440004",
    "learning_objective_id": "LO-UUID-P3-F-1.1",
    "is_primary": true
  },
  {
    "question_part_id": "772e8400-e29b-41d4-a716-446655440004",
    "learning_objective_id": "LO-UUID-P3-F-2.1",
    "is_primary": false
  }
]
```

---

### Example 4: Algebraic Expression (Symbolic Equivalence)

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440007",
  "title": "Simplifying Expressions",
  "question_text": "Simplify the expression: x + 2x + 3",
  "question_type": "short_answer",
  "difficulty": "medium",
  "marks": 2.0,
  "time_limit_seconds": 120,
  "is_multipart": false,
  "type_data": {
    "acceptable_answers": ["3x + 3", "3(x + 1)", "3 + 3x"],
    "answer_type": "text",
    "case_sensitive": false,
    "max_length": 100,
    "match_type": "equivSymbolic"
  },
  "metadata": {
    "hint": "Combine like terms.",
    "explanation": "x + 2x = 3x, so the simplified expression is 3x + 3 or 3(x + 1)."
  },
  "status": "active",
  "version": 1,
  "created_at": "2025-10-13T17:00:00Z",
  "updated_at": "2025-10-13T17:00:00Z",
  "created_by": "reviewer@example.com"
}
```

---

## Image Display Guidelines

### Overview

Images are displayed as block-level elements in simple, predictable positions:
- **Before question text** (default) - "shown above", "in the diagram", "the shape below"
- **After question text** - "as shown below", "illustrated in the figure"
- **As MCQ options** - Image-based answer choices

This approach eliminates parsing complexity, improves mobile rendering, and simplifies content authoring.

**Key Principle:** Question text uses natural language references ("the triangle shown above") instead of complex placeholder syntax.

---

### Position Types

| Position | Description | When to Use |
|----------|-------------|-------------|
| `before_text` | Image displays above question text (default) | Diagrams, charts, shapes that questions refer to |
| `after_text` | Image displays below question text | Illustrations that clarify the question, optional reference materials |
| `option` | Image is an MCQ option choice | Visual identification questions, shape/pattern selection |
| `hint` | Image displays below hint | Hint requires an image |
| `explanation` | Image displays below explanation | Explanation requires an image |

---

### Example 1: Simple Diagram Question (before_text)

**Question:**
```json
{
  "id": "q-001",
  "question_text": "What is the length of side AB in the triangle shown above?",
  "question_type": "short_answer",
  "type_data": {
    "acceptable_answers": ["5 cm", "5cm"],
    "answer_type": "text",
    "match_type": "equivLiteral"
  }
}
```

**Image Link:**
```json
{
  "image_id": "img-001",
  "question_id": "q-001",
  "placeholder_ref": "triangle_diagram",
  "position": "before_text",
  "display_order": 1
}
```

**Rendered Output:**
```
[IMAGE: Right-angled triangle with sides labeled A, B, C]

What is the length of side AB in the triangle shown above?
```

---

### Example 2: Multiple Images Before Question

**Question:**
```json
{
  "id": "q-002",
  "question_text": "Study the two shapes shown above. Which shape has more sides?",
  "question_type": "mcq",
  "type_data": {
    "options": [
      {"id": "a", "text": "Shape A", "is_correct": false},
      {"id": "b", "text": "Shape B", "is_correct": true},
      {"id": "c", "text": "They have the same number", "is_correct": false}
    ],
    "allow_multiple": false
  }
}
```

**Image Links:**
```json
[
  {
    "image_id": "img-010",
    "question_id": "q-002",
    "placeholder_ref": "shape_a",
    "position": "before_text",
    "display_order": 1
  },
  {
    "image_id": "img-011",
    "question_id": "q-002",
    "placeholder_ref": "shape_b",
    "position": "before_text",
    "display_order": 2
  }
]
```

**Rendered Output:**
```
[IMAGE: Pentagon labeled "Shape A"]  [IMAGE: Hexagon labeled "Shape B"]

Study the two shapes shown above. Which shape has more sides?
A. Shape A
B. Shape B ✓
C. They have the same number
```

---

### Example 3: Image After Question Text (after_text)

**Question:**
```json
{
  "id": "q-003",
  "question_text": "Draw a rectangle with length 5 cm and width 3 cm. You may use the grid provided below.",
  "question_type": "short_answer",
  "type_data": {
    "acceptable_answers": ["completed"],
    "answer_type": "text",
    "match_type": "equivLiteral"
  }
}
```

**Image Link:**
```json
{
  "image_id": "img-020",
  "question_id": "q-003",
  "placeholder_ref": "blank_grid",
  "position": "after_text",
  "display_order": 1
}
```

**Rendered Output:**
```
Draw a rectangle with length 5 cm and width 3 cm. You may use the grid provided below.

[IMAGE: Blank grid paper]
```

---

### Example 4: Multi-Part Question with Part-Specific Images

**Parent Question:**
```json
{
  "id": "q-004",
  "question_text": "Answer the following questions about the coordinate grid shown above.",
  "is_multipart": true
}
```

**Parent Image:**
```json
{
  "image_id": "img-030",
  "question_id": "q-004",
  "placeholder_ref": "coordinate_grid",
  "position": "before_text",
  "display_order": 1
}
```

**Part A:**
```json
{
  "id": "qp-004-a",
  "question_id": "q-004",
  "part_id": "a",
  "part_sequence": 1,
  "part_text": "What are the coordinates of point C?",
  "question_type": "short_answer",
  "type_data": {
    "acceptable_answers": ["(5, 3)", "(5,3)"],
    "answer_type": "text",
    "match_type": "equivLiteral"
  }
}
```

**Part B with Additional Image:**
```json
{
  "id": "qp-004-b",
  "question_id": "q-004",
  "part_id": "b",
  "part_sequence": 2,
  "part_text": "Plot the point D at (2, 6) on the blank grid shown below.",
  "question_type": "short_answer",
  "type_data": {
    "acceptable_answers": ["completed"],
    "answer_type": "text",
    "match_type": "equivLiteral"
  }
}
```

**Part B Image:**
```json
{
  "image_id": "img-031",
  "question_part_id": "qp-004-b",
  "placeholder_ref": "blank_grid",
  "position": "after_text",
  "display_order": 1
}
```

**Rendered Output:**
```
[IMAGE: Coordinate grid with rectangle ABCD plotted]

Answer the following questions about the coordinate grid shown above.

(a) What are the coordinates of point C?

(b) Plot the point D at (2, 6) on the blank grid shown below.

    [IMAGE: Blank coordinate grid]
```

---

### Example 5: Image-Based MCQ Options

**Question:**
```json
{
  "id": "q-005",
  "question_text": "Which shape is a rectangle?",
  "question_type": "mcq",
  "type_data": {
    "options": [
      {"id": "a", "text": "Option A", "is_correct": false},
      {"id": "b", "text": "Option B", "is_correct": true},
      {"id": "c", "text": "Option C", "is_correct": false},
      {"id": "d", "text": "Option D", "is_correct": false}
    ],
    "allow_multiple": false
  }
}
```

**Image Links for Options:**
```json
[
  {
    "image_id": "img-040",
    "question_id": "q-005",
    "placeholder_ref": "option_a_circle",
    "position": "option",
    "display_order": 1
  },
  {
    "image_id": "img-041",
    "question_id": "q-005",
    "placeholder_ref": "option_b_rectangle",
    "position": "option",
    "display_order": 2
  },
  {
    "image_id": "img-042",
    "question_id": "q-005",
    "placeholder_ref": "option_c_triangle",
    "position": "option",
    "display_order": 3
  },
  {
    "image_id": "img-043",
    "question_id": "q-005",
    "placeholder_ref": "option_d_pentagon",
    "position": "option",
    "display_order": 4
  }
]
```

**Rendered Output:**
```
Which shape is a rectangle?

A. [IMAGE: Circle]
B. [IMAGE: Rectangle] ✓
C. [IMAGE: Triangle]
D. [IMAGE: Pentagon]
```

**Note:** When `position = 'option'`, the image is matched to the corresponding option by `display_order` (1→a, 2→b, 3→c, 4→d).

---

### Example 6: Chart/Graph Question

**Question:**
```json
{
  "id": "q-006",
  "question_text": "The bar chart shows the favorite ice cream flavors of students in Primary 4. How many students prefer chocolate?",
  "question_type": "short_answer",
  "type_data": {
    "acceptable_answers": ["15"],
    "answer_type": "numeric",
    "match_type": "equivValue"
  }
}
```

**Image Link:**
```json
{
  "image_id": "img-050",
  "question_id": "q-006",
  "placeholder_ref": "ice_cream_bar_chart",
  "position": "before_text",
  "display_order": 1
}
```

**Rendered Output:**
```
[IMAGE: Bar chart showing ice cream preferences - Chocolate: 15, Vanilla: 12, Strawberry: 8, Mint: 5]

The bar chart shows the favorite ice cream flavors of students in Primary 4. 
How many students prefer chocolate?
```

---

### Example 7: Pattern Question with Multiple Images

**Question:**
```json
{
  "id": "q-007",
  "question_text": "Look at the three shapes in the pattern shown above. What comes next?",
  "question_type": "mcq",
  "type_data": {
    "options": [
      {"id": "a", "text": "Red circle", "is_correct": false},
      {"id": "b", "text": "Blue circle", "is_correct": true},
      {"id": "c", "text": "Green circle", "is_correct": false}
    ],
    "allow_multiple": false
  }
}
```

**Image Links (Pattern Sequence):**
```json
[
  {
    "image_id": "img-060",
    "question_id": "q-007",
    "placeholder_ref": "pattern_red_circle",
    "position": "before_text",
    "display_order": 1
  },
  {
    "image_id": "img-061",
    "question_id": "q-007",
    "placeholder_ref": "pattern_blue_circle",
    "position": "before_text",
    "display_order": 2
  },
  {
    "image_id": "img-062",
    "question_id": "q-007",
    "placeholder_ref": "pattern_red_circle_2",
    "position": "before_text",
    "display_order": 3
  }
]
```

**Rendered Output:**
```
[🔴] [🔵] [🔴]

Look at the three shapes in the pattern shown above. What comes next?
A. Red circle
B. Blue circle ✓
C. Green circle
```

---

### Example 8: Reference Material Image (after_text)

**Question:**
```json
{
  "id": "q-008",
  "question_text": "Calculate the area of a circle with radius 7 cm. Use the formula sheet provided below if needed.",
  "question_type": "short_answer",
  "type_data": {
    "acceptable_answers": ["153.94", "154"],
    "answer_type": "numeric",
    "match_type": "equivValue"
  },
  "metadata": {
    "explanation": "Area = πr² = π × 7² = π × 49 ≈ 153.94 cm²"
  }
}
```

**Image Link:**
```json
{
  "image_id": "img-070",
  "question_id": "q-008",
  "placeholder_ref": "formula_sheet",
  "position": "after_text",
  "display_order": 1
}
```

**Rendered Output:**
```
Calculate the area of a circle with radius 7 cm. Use the formula sheet provided below if needed.

[IMAGE: Formula sheet showing Area = πr², Circumference = 2πr, etc.]
```

---

## Common Question Text Patterns

Use these natural language patterns when writing question text:

| Pattern | Image Position | Example |
|---------|---------------|---------|
| "shown above" | before_text | "What is the perimeter of the shape shown above?" |
| "in the diagram" | before_text | "Find the value of x in the diagram." |
| "the figure shows" | before_text | "The figure shows a rectangle. Calculate its area." |
| "refer to the chart" | before_text | "Refer to the chart. How many students chose soccer?" |
| "shown below" | after_text | "Draw the reflection as shown below." |
| "use the grid below" | after_text | "Plot the points using the grid below." |
| "provided below" | after_text | "Use the formula sheet provided below." |

---

## Rendering Implementation

### Display Logic

```python
def render_question(question, images):
    """
    Simple block-level rendering of questions with images.
    """
    output = []
    
    # 1. Display all before_text images
    before_images = [img for img in images if img.position == 'before_text']
    before_images.sort(key=lambda x: x.display_order)
    for img in before_images:
        output.append(render_image(img))
    
    # 2. Display question text
    output.append(f"<p>{question.question_text}</p>")
    
    # 3. Display all after_text images
    after_images = [img for img in images if img.position == 'after_text']
    after_images.sort(key=lambda x: x.display_order)
    for img in after_images:
        output.append(render_image(img))
    
    # 4. Display options (with option images if present)
    if question.question_type == 'mcq':
        output.append(render_mcq_options(question, images))
    
    return '\n'.join(output)

def render_mcq_options(question, images):
    """
    Render MCQ options, replacing text with images where position='option'.
    """
    option_images = {img.display_order: img for img in images if img.position == 'option'}
    options_html = []
    
    for i, option in enumerate(question.type_data['options'], start=1):
        if i in option_images:
            # Replace text with image
            options_html.append(f"{option['id'].upper()}. {render_image(option_images[i])}")
        else:
            # Display text normally
            options_html.append(f"{option['id'].upper()}. {option['text']}")
    
    return '<ul>' + '\n'.join(f'<li>{opt}</li>' for opt in options_html) + '</ul>'

def render_image(image):
    """
    Render a single image with alt text and responsive sizing.
    """
    return f'<img src="{image.file_path}" alt="{image.alt_text}" class="question-image" />'
```

### CSS Styling

```css
/* Simple, responsive image styling */
.question-image {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* Multiple images side-by-side on larger screens */
.images-before-text {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .images-before-text {
    flex-direction: column;
  }
}

/* Option images should be smaller */
.option-image {
  max-width: 200px;
  height: auto;
  display: inline-block;
  vertical-align: middle;
}
```

---

## Benefits of Block-Level Approach

✅ **Simple Implementation:** No text parsing, no complex layout algorithms  
✅ **Mobile-Friendly:** Images stack naturally on small screens  
✅ **Accessible:** Linear tab order, clear screen reader flow  
✅ **Easy Authoring:** Teachers write natural question text  
✅ **Predictable Layout:** Consistent rendering across devices  
✅ **Fast Rendering:** No regex parsing or placeholder replacement  
✅ **Future-Proof:** Can add inline support later if needed without breaking existing questions

---

## Future Considerations

If inline image placement becomes necessary in the future:
1. Add `position = 'inline'` enum value
2. Support `{{image:ref}}` syntax in question text
3. Implement parser/renderer for inline replacement
4. This won't break existing questions (backward compatible)

For now, 95%+ of real questions work perfectly with block-level positioning.

---

## Indexing Strategy

### Primary Query Indexes

**Questions Table:**
```sql
-- Filter by common attributes
CREATE INDEX idx_questions_status ON questions(status) WHERE status = 'active';
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_marks ON questions(marks);
CREATE INDEX idx_questions_is_multipart ON questions(is_multipart);
CREATE INDEX idx_questions_question_type ON questions(question_type);

-- Composite indexes for common filter combinations
CREATE INDEX idx_questions_status_difficulty ON questions(status, difficulty) WHERE status = 'active';
CREATE INDEX idx_questions_status_marks ON questions(status, marks) WHERE status = 'active';
CREATE INDEX idx_questions_status_multipart ON questions(status, is_multipart) WHERE status = 'active';

-- Timestamps for sorting
CREATE INDEX idx_questions_created_at ON questions(created_at);
CREATE INDEX idx_questions_updated_at ON questions(updated_at);
```

**Learning Objectives Table:**
```sql
-- Primary filters for worksheet generation
CREATE INDEX idx_learning_objectives_subject ON learning_objectives(subject);
CREATE INDEX idx_learning_objectives_grade_level ON learning_objectives(grade_level);
CREATE INDEX idx_learning_objectives_topic ON learning_objectives(topic);
CREATE INDEX idx_learning_objectives_code ON learning_objectives(code);

-- Composite for hierarchy queries (most common)
CREATE INDEX idx_learning_objectives_hierarchy 
  ON learning_objectives(subject, grade_level, topic, subtopic);
  
CREATE INDEX idx_learning_objectives_version 
  ON learning_objectives(curriculum_version, effective_from, effective_to);
```

**Question-to-LO Mappings:**
```sql
-- Critical for filtering by curriculum
CREATE INDEX idx_qlo_question_id ON question_learning_objectives(question_id);
CREATE INDEX idx_qlo_learning_objective_id ON question_learning_objectives(learning_objective_id);
CREATE INDEX idx_qlo_is_primary ON question_learning_objectives(is_primary) WHERE is_primary = TRUE;

-- Composite for common join patterns
CREATE INDEX idx_qlo_lo_question ON question_learning_objectives(learning_objective_id, question_id);

-- Question part mappings
CREATE INDEX idx_qplo_question_part_id ON question_part_learning_objectives(question_part_id);
CREATE INDEX idx_qplo_learning_objective_id ON question_part_learning_objectives(learning_objective_id);
```

---

### Search & Filtering Indexes

```sql
-- Full-text search on question text
CREATE INDEX idx_questions_question_text_gin 
  ON questions USING gin(to_tsvector('english', question_text));
  
CREATE INDEX idx_question_parts_part_text_gin 
  ON question_parts USING gin(to_tsvector('english', part_text));

-- Full-text search on learning objectives
CREATE INDEX idx_learning_objectives_description_gin 
  ON learning_objectives USING gin(to_tsvector('english', description));
```

---

### Relationship Indexes

```sql
-- Question parts
CREATE INDEX idx_question_parts_question_id ON question_parts(question_id);
CREATE INDEX idx_question_parts_question_type ON question_parts(question_type);
CREATE INDEX idx_question_parts_part_sequence ON question_parts(question_id, part_sequence);

-- Images
CREATE INDEX idx_question_images_question_id ON question_images(question_id);
CREATE INDEX idx_question_images_question_part_id ON question_images(question_part_id);
CREATE INDEX idx_question_images_image_id ON question_images(image_id);
CREATE INDEX idx_question_images_placeholder_ref ON question_images(placeholder_ref) WHERE placeholder_ref IS NOT NULL;
CREATE INDEX idx_question_images_position ON question_images(position);

-- Custom tags
CREATE INDEX idx_question_tags_question_id ON question_tags(question_id);
CREATE INDEX idx_question_tags_tag_id ON question_tags(tag_id);
CREATE INDEX idx_custom_tags_tag_name ON custom_tags(tag_name);
CREATE INDEX idx_custom_tags_tag_category ON custom_tags(tag_category);

-- Audit log
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

---

### JSONB Indexes

```sql
-- Index for querying type_data
CREATE INDEX idx_questions_type_data_gin ON questions USING gin(type_data);
CREATE INDEX idx_question_parts_type_data_gin ON question_parts USING gin(type_data);

-- Index for metadata fields
CREATE INDEX idx_questions_metadata_gin ON questions USING gin(metadata);

-- Specific JSONB path indexes for common queries (PostgreSQL 14+)
-- Find questions with hints
CREATE INDEX idx_questions_has_hint 
  ON questions((metadata->>'hint')) WHERE metadata->>'hint' IS NOT NULL;

-- Find MCQs with multiple correct answers
CREATE INDEX idx_questions_allow_multiple 
  ON questions((type_data->>'allow_multiple')) 
  WHERE question_type = 'mcq' AND (type_data->>'allow_multiple')::boolean = TRUE;
```

---

## Common Query Patterns

### Query 1: Generate Worksheet by Learning Objectives
```sql
-- Find all active questions for P4 Decimals Rounding
SELECT DISTINCT q.*
FROM questions q
JOIN question_learning_objectives qlo ON q.id = qlo.question_id
JOIN learning_objectives lo ON qlo.learning_objective_id = lo.id
WHERE q.status = 'active'
  AND lo.grade_level = 'P4'
  AND lo.topic = 'Decimals'
  AND lo.subtopic = 'Rounding'
ORDER BY q.marks, q.difficulty;
```

---

### Query 2: Random Selection with Constraints
```sql
-- Select 5 random easy MCQs from P3 Fractions
SELECT q.*
FROM questions q
JOIN question_learning_objectives qlo ON q.id = qlo.question_id
JOIN learning_objectives lo ON qlo.learning_objective_id = lo.id
WHERE q.status = 'active'
  AND q.question_type = 'mcq'
  AND q.difficulty = 'easy'
  AND lo.grade_level = 'P3'
  AND lo.topic = 'Fractions'
ORDER BY RANDOM()
LIMIT 5;
```

---

### Query 3: Get Complete Question with Parts and Images
```sql
-- Get question with all parts, images, and tags
SELECT 
  q.*,
  json_agg(DISTINCT jsonb_build_object(
    'id', qp.id,
    'part_id', qp.part_id,
    'part_sequence', qp.part_sequence,
    'part_text', qp.part_text,
    'question_type', qp.question_type,
    'marks', qp.marks,
    'type_data', qp.type_data,
    'metadata', qp.metadata
  ) ORDER BY qp.part_sequence) FILTER (WHERE qp.id IS NOT NULL) as parts,
  json_agg(DISTINCT jsonb_build_object(
    'image', i,
    'placeholder_ref', qi.placeholder_ref,
    'context', qi.context,
    'display_order', qi.display_order
  ) ORDER BY qi.display_order) FILTER (WHERE i.id IS NOT NULL) as images,
  json_agg(DISTINCT lo.*) FILTER (WHERE lo.id IS NOT NULL) as learning_objectives
FROM questions q
LEFT JOIN question_parts qp ON q.id = qp.question_id
LEFT JOIN question_images qi ON q.id = qi.question_id OR qp.id = qi.question_part_id
LEFT JOIN images i ON qi.image_id = i.id
LEFT JOIN question_learning_objectives qlo ON q.id = qlo.question_id
LEFT JOIN learning_objectives lo ON qlo.learning_objective_id = lo.id
WHERE q.id = $1
GROUP BY q.id;
```

---

### Query 4: Full-Text Search
```sql
-- Search questions by text
SELECT q.*, 
       ts_rank(to_tsvector('english', q.question_text), query) AS rank
FROM questions q,
     to_tsquery('english', 'decimal & round') query
WHERE to_tsvector('english', q.question_text) @@ query
  AND q.status = 'active'
ORDER BY rank DESC
LIMIT 20;
```

---

### Query 5: Find Questions by Curriculum Version
```sql
-- Find all questions tagged with specific curriculum version
SELECT DISTINCT q.*
FROM questions q
JOIN question_learning_objectives qlo ON q.id = qlo.question_id
JOIN learning_objectives lo ON qlo.learning_objective_id = lo.id
WHERE lo.curriculum_version = 'sg-primary-math-2025'
  AND q.status = 'active'
ORDER BY q.created_at DESC;
```

---

## Entity Relationship Diagram

```
questions (1) ──< (M) question_parts
    |                      |
    |                      |
   (M)                    (M)
    |                      |
    └──< question_learning_objectives >──┐
                 |                        |
                (M)                      (M)
                 |                        |
    ┌────────────┴────────────────────────┘
    |
learning_objectives

questions (1) ──< (M) question_images >──< (M) images
    |
question_parts (1) ──< (M) question_images (shared junction)

questions (1) ──< (M) question_tags >──< (M) custom_tags
```

**Key Relationships:**

1. **Questions → Question Parts**: One-to-many (only for multi-part questions)
2. **Questions → Learning Objectives**: Many-to-many via `question_learning_objectives`
3. **Question Parts → Learning Objectives**: Many-to-many via `question_part_learning_objectives`
4. **Questions/Parts → Images**: Many-to-many via `question_images` (XOR constraint)
5. **Questions → Custom Tags**: Many-to-many via `question_tags`

---

## Data Integrity Rules

### Database Constraints

| Constraint Type | Details |
|----------------|---------|
| **Foreign Keys** | All relationships use `ON DELETE CASCADE` for automatic cleanup |
| **Check Constraints** | `difficulty` ∈ {easy, medium, hard}, `marks` > 0, `status` ∈ {draft, active, archived} |
| **Unique Constraints** | `learning_objectives.code`, `(question_id, part_id)`, `(question_id, part_sequence)`, `(question_id, learning_objective_id)` |
| **Conditional Constraints** | Multi-part questions: `question_type` and `type_data` must be NULL |
| **JSONB Validation** | Application-layer validation via Pydantic models |
| **XOR Constraints** | `question_images` linked to question OR part, not both |

---

### Application-Level Validation Rules

**On Save/Approve:**

1. **Required Fields:**
   - Questions: `question_text`, `marks` (>0), `difficulty`, `status`
   - Single-part: `question_type` required, `type_data` must match schema
   - Multi-part: At least 1 part required

2. **Type-Specific Validation:**
   - MCQ: 2-6 options, correct answer count matches `allow_multiple` setting
   - Short Answer: At least 1 acceptable answer, valid `match_type`

3. **Curriculum Tagging:**
   - At least 1 learning objective required (either on question or parts)
   - Exactly 1 tag marked as `is_primary=true` per question/part

4. **Part Sequencing:**
   - Part sequences must start at 1 and be sequential (no gaps)
   - Part IDs should match conventional labeling (a, b, c or 1, 2, 3)

5. **Image References:**
   - Question text should use natural references ("shown above", "in the diagram") instead of placeholders
   - Images must have valid `file_path` and `storage_type`
   - `placeholder_ref` is optional and used for internal tracking only
   - For image-based MCQ options, `display_order` matches option position (1→a, 2→b, etc.)

6. **Marks Validation:**
   - Marks must be positive decimals (e.g., 0.5, 1.0, 1.5, 2.0)
   - For multi-part questions: Sum of part marks should equal total question marks

---

## Storage Estimates

| Entity | Avg Size per Record | Expected Volume (Year 1) | Total Storage |
|--------|---------------------|---------------------------|---------------|
| questions | 2-4 KB | 10,000 | ~40 MB |
| question_parts | 1-3 KB | 15,000 | ~45 MB |
| learning_objectives | 0.5 KB | 500 | ~0.25 MB |
| question_learning_objectives | 0.1 KB | 30,000 | ~3 MB |
| question_part_learning_objectives | 0.1 KB | 20,000 | ~2 MB |
| images (metadata only) | 0.5 KB | 5,000 | ~2.5 MB |
| question_images | 0.2 KB | 7,000 | ~1.4 MB |
| custom_tags | 0.1 KB | 100 | ~0.01 MB |
| question_tags | 0.1 KB | 5,000 | ~0.5 MB |
| audit_log | 1 KB | 100,000 | ~100 MB |
| **Total (Database)** | | | **~195 MB** |
| **Images (Object Storage)** | 50-200 KB | 5,000 | **~500 MB** |

**Notes:**

- JSONB fields (`type_data`, `metadata`) are automatically compressed by PostgreSQL
- Images stored in S3/GCS; only metadata stored in database
- Indexes add approximately 30-40% overhead to base table size
- Audit log retention: 7 years for compliance (will grow to ~700 MB over time)
- Object storage costs separate from database storage

**Growth Projections:**

- Year 2: ~400 MB database, ~1 GB object storage
- Year 3: ~600 MB database, ~1.5 GB object storage
- Year 5: ~1 GB database, ~2.5 GB object storage

---

## Appendix: Key Design Decisions

### 1. Multi-part Question Structure
**Decision:** Use separate `question_parts` table rather than nested JSONB  
**Rationale:** Enables efficient querying, filtering, and tagging at part level; supports independent part reuse in future

### 2. JSONB for Type Data
**Decision:** Store MCQ options and short answer data as JSONB  
**Rationale:** Flexible schema evolution; natural fit for heterogeneous question types; PostgreSQL GIN indexes enable efficient querying

### 3. Flattened Curriculum Hierarchy
**Decision:** Single `learning_objectives` table with all hierarchy levels  
**Rationale:** Simpler queries; avoids complex joins; easier to version entire curriculum

### 4. Learnosity Match Types
**Decision:** Adopt Learnosity scoring terminology (`equivLiteral`, `equivSymbolic`, `equivValue`, `stringMatch`)  
**Rationale:** Industry-standard; enables future integration with Learnosity or similar systems; well-documented behavior

### 5. Image Placeholder References
**Decision:** Use semantic placeholders (e.g., `{{image:triangle}}`) rather than numeric IDs  
**Rationale:** More readable for content authors; self-documenting; survives image replacements

### 6. Cascade Deletes
**Decision:** Use `ON DELETE CASCADE` for all foreign keys  
**Rationale:** Ensures referential integrity; simplifies deletion logic; prevents orphaned records

### 7. Part Sequence vs Part Number
**Decision:** Use `part_sequence` for ordering instead of `part_number`  
**Rationale:** `part_sequence` is clearer for ordering logic; avoids confusion with `part_id` which may be non-numeric (a, b, c)

### 8. Block-Level Images (No Inline Placeholders)
**Decision:** Images display as block elements (before/after text, or as options) rather than inline within text  
**Rationale:** 
- Eliminates rendering complexity (no text parsing, no complex layout)
- Better mobile/responsive experience (images stack naturally)
- Improved accessibility (linear tab order, clear screen reader flow)
- Easier content authoring (teachers write natural references like "shown above")
- Faster implementation (weeks vs. months)
- Can add inline support later if needed without breaking existing questions

---

**End of Document**