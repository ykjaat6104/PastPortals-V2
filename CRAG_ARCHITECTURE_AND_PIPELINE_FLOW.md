# CRAG Architecture and Pipeline Flow

## Overview

**CRAG (Correction + Retrieval-Augmented Generation)** is the fact-checking pipeline used in PastPortals v2 to ground generated answers in retrieved context and reduce hallucinations.

It sits in the multimodal analysis path and adds a retrieval, validation, and correction layer before the final response is returned.

## Architecture

### 4-Stage Pipeline

```text
┌──────────────┐
│  Query Input │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 1: RETRIEVAL                  │
│ - Search FAISS vector database      │
│ - Fall back to Wikipedia search     │
│ - Return top-k relevant contexts    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 2: GENERATION                 │
│ - Use retrieved context             │
│ - Generate response with Gemini     │
│ - Keep output grounded in sources   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 3: VALIDATION                 │
│ - Extract key claims                │
│ - Compare claims with source text   │
│ - Produce confidence score          │
│ - Collect validation issues         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 4: CORRECTION                 │
│ - Rewrite low-confidence responses  │
│ - Remove unverified claims          │
│ - Preserve supported facts only     │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Final Response     │
│  Fact-checked       │
└─────────────────────┘
```

## Pipeline Flow

### 1. Retrieval

`backend/utils/crag_utils.py` starts by searching the vector database through `backend/utils/vector_utils.py`.

If the FAISS index is unavailable, the pipeline falls back to Wikipedia-based context lookup so the request can still complete.

### 2. Generation

The retrieved context is passed into Gemini with a grounded prompt. The model is asked to answer using only the supplied evidence and to avoid unsupported claims.

### 3. Validation

The generated response is checked against the retrieved context.

The validator looks for:

- unsupported factual claims
- suspicious numbers or dates
- weakly grounded statements
- uncertainty that should be corrected or clarified

### 4. Correction

If validation confidence drops below the configured threshold, the pipeline rewrites the response.

The correction stage keeps verified facts, removes uncertain statements, and returns a more reliable final answer.

## Core Components

### CRAGValidator

File: `backend/utils/crag_utils.py`

The `CRAGValidator` class orchestrates the full pipeline.

Key methods:

- `retrieve(query, index, text_map, k=5)`
- `generate(query, context, temperature=0.6)`
- `validate_facts(response, context, query)`
- `correct(response, issues, context, query)`
- `execute_pipeline(query, index, text_map, extracted_text="")`

### API Integration

File: `backend/routes/multimodal_routes.py`

The `/api/multimodal/analyze` endpoint now calls the CRAG pipeline and returns CRAG metadata alongside the normal multimodal response.

Typical response fields include:

```json
{
  "success": true,
  "response": "Final fact-checked response",
  "crag": {
    "applied": true,
    "validation_passed": true,
    "confidence_score": 0.85,
    "validation_issues": [],
    "stages_completed": 4
  }
}
```

### Supporting Utilities

- `backend/utils/vector_utils.py` handles FAISS loading and search.
- `backend/utils/ai_utils.py` configures Gemini access and embeddings.
- `backend/utils/__init__.py` exports the CRAG utilities for imports.

## Configuration

The pipeline is tuned for balanced generation and conservative correction.

Recommended defaults:

- confidence threshold: `0.7`
- generation temperature: `0.6`
- max tokens: `1500`
- max validation attempts: `2`
- retrieval top-k: `5`

## Validation Metrics

Confidence is used to decide whether the generated response is trustworthy enough to return directly.

If the confidence score falls below the threshold, the correction stage is triggered.

## Testing

### Existing Test Coverage

The repository currently includes multimodal test coverage that exercises the surrounding analysis path:

- `backend/tests/test_multimodal_utils.py`
- `backend/tests/test_multimodal_routes.py`

These files validate document extraction, request handling, metadata, and response behavior around the CRAG-enabled endpoint.

### Recommended CRAG Test Cases

If you want dedicated CRAG tests, the pipeline should be covered with cases for:

- retrieval fallback when FAISS is missing
- validation failures for unsupported claims
- correction behavior when confidence is low
- successful pass-through when context is strong
- `/api/multimodal/analyze` response shape when CRAG is applied

### Useful Commands

```powershell
# Syntax checks
python -m py_compile backend/utils/crag_utils.py
python -m py_compile backend/routes/multimodal_routes.py

# Existing multimodal tests
pytest backend/tests/test_multimodal_utils.py -v
pytest backend/tests/test_multimodal_routes.py -v
```

## Troubleshooting

### Vector DB Not Found

If the FAISS index or text map is missing, the pipeline falls back to alternate retrieval instead of failing outright.

### Low Confidence Scores

Usually this means the retrieved context is thin, vague, or unrelated. Improving the knowledge base usually helps more than loosening validation.

### Frequent Corrections

If valid responses are being rewritten too often, reduce the strictness of the validation rules or improve retrieval quality.

## Summary

CRAG adds a grounded verification layer to multimodal analysis. The result is a response flow that retrieves evidence, generates an answer, validates it, and corrects it when necessary before returning the final output.
