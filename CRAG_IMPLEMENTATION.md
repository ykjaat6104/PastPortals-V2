# CRAG Implementation Documentation

## Overview

**CRAG (Correction + Retrieval-Augmented Generation)** is a 4-stage pipeline implemented in PastPortals v2 to ensure accurate, fact-checked responses while minimizing AI hallucinations.

## Architecture

### 4-Stage Pipeline

```
┌──────────────┐
│  Query Input │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 1: RETRIEVAL                  │
│ - Search vector database (FAISS)    │
│ - Fallback to Wikipedia search      │
│ - Return top-k relevant contexts    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 2: GENERATION                 │
│ - Use retrieved context             │
│ - Generate response with Gemini 2.5 │
│ - Temperature: 0.6 (balanced)       │
│ - Max tokens: 1500                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 3: VALIDATION                 │
│ - Extract key claims                │
│ - Verify against source context     │
│ - Calculate confidence score        │
│ - Identify validation issues        │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Stage 4: CORRECTION                 │
│ - If confidence < threshold (0.7)   │
│ - Rewrite response                  │
│ - Remove unverified claims          │
│ - Keep source-verified facts only   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Final Response     │
│ (Fact-Checked)      │
└─────────────────────┘
```

## Components

### 1. CRAGValidator Class (`backend/utils/crag_utils.py`)

**Purpose:** Orchestrates the entire CRAG pipeline

**Key Methods:**

- **`retrieve(query, index, text_map, k=5)`**
  - Retrieves relevant context from knowledge base
  - Uses FAISS vector search with semantic similarity
  - Falls back to Wikipedia if vector DB unavailable
  - Returns top-k most relevant documents

- **`generate(query, context, temperature=0.6)`**
  - Generates response based on retrieved context
  - Uses Google Gemini 2.5 Flash model
  - Context-aware prompt engineering
  - Enforces grounding in provided context

- **`validate_facts(response, context, query)`**
  - Validates generated claims against source context
  - Checks for:
    - Unverified claims
    - Unsupported statistics/numbers
    - Uncertainty phrases
  - Returns confidence score (0.0-1.0)
  - Lists identified issues

- **`correct(response, issues, context, query)`**
  - Fact-checks and rewrites response if needed
  - Removes unsupported claims
  - Preserves verified information
  - Maintains professional tone

- **`execute_pipeline(query, index, text_map, extracted_text="")`**
  - Main entry point executing all 4 stages
  - Returns comprehensive results with:
    - Retrieved context
    - Generated response
    - Validation confidence score
    - Corrected response
    - CRAG metrics

### 2. Integration with Multimodal Routes

**File:** `backend/routes/multimodal_routes.py`

**Modified Endpoint:** `POST /api/multimodal/analyze`

**Response Structure:**

```json
{
  "success": true,
  "mode": "document|image|video|voice",
  "method": "extraction_method",
  "metadata": { ... },
  "extracted_text": "...",
  "notes": [...],
  "response": "Final fact-checked response",
  "related_topics": [...],
  "crag": {
    "applied": true,
    "validation_passed": true,
    "confidence_score": 0.85,
    "validation_issues": [],
    "stages_completed": 4
  }
}
```

## Validation Metrics

### Confidence Score Calculation

```python
confidence = 1.0
confidence -= (unverified_claims_count * 0.15)
confidence -= (unsupported_facts_count * 0.1)
confidence = clamp(confidence, 0.0, 1.0)
```

### Validation Passes If:
- `confidence_score >= 0.7` (default threshold)
- No critical validation issues
- At least 50% of claims have source verification

### Triggers Correction If:
- `confidence_score < 0.7`
- Validation attempts < 2 (prevents infinite loops)
- Issues identified in validation stage

## Example Usage

### Direct Usage

```python
from utils.crag_utils import apply_crag
from utils.vector_utils import load_vector_db

# Load vector database
index, text_map = load_vector_db('path/to/faiss_index.bin', 'path/to/text_map.json')

# Apply CRAG pipeline
results = apply_crag(
    query="What was the significance of the Egyptian pyramids?",
    index=index,
    text_map=text_map,
    extracted_text=""  # Optional user document content
)

# Access results
final_response = results['final_response']
confidence = results['stage_3_validation']['confidence_score']
issues = results['stage_3_validation']['issues']
```

### Through API Endpoint

```bash
curl -X POST http://localhost:5000/api/multimodal/analyze \
  -F "question=Tell me about ancient Rome" \
  -F "file=@document.pdf"
```

## Features

### ✅ Hallucination Prevention

- Grounds all responses in retrieved context
- Validates claims against source documents
- Removes unsupported statements
- Provides confidence metrics

### ✅ Adaptive Correction

- Multi-stage validation process
- Fact-checking with source attribution
- Intelligent rewriting without losing meaning
- Preserves verified historical context

### ✅ Fallback Support

- Works with or without vector database
- Falls back to Wikipedia for context retrieval
- Graceful degradation if components unavailable
- Always provides response (CRAG or fallback)

### ✅ Metrics & Transparency

- Confidence scores (0.0-1.0)
- Validation issue reporting
- Pipeline stage completion tracking
- Debug information in response

## Configuration

### Threshold Settings

```python
# In backend/utils/crag_utils.py
CONFIDENCE_THRESHOLD = 0.7  # Triggers correction if below this
MAX_VALIDATION_ATTEMPTS = 2  # Prevents infinite loops
```

### Model Settings

```python
# In generate() method
temperature = 0.6  # Balanced (0=deterministic, 1=random)
max_tokens = 1500  # Response length limit
```

## Performance Considerations

### Latency

| Stage | Typical Latency |
|-------|-----------------|
| Retrieval | 50-200ms |
| Generation | 2-5s |
| Validation | 100-300ms |
| Correction (if needed) | 2-4s |
| **Total** | **4-10s** |

### Optimization Tips

1. **Cache embeddings** for frequent queries
2. **Batch queries** when possible
3. **Use smaller context window** (k=3-5 results)
4. **Adjust temperature** based on use case
5. **Monitor confidence scores** for pattern analysis

## Testing

### Unit Tests Available

```bash
# Test CRAG validator
pytest backend/tests/test_crag_validator.py -v

# Test multimodal routes with CRAG
pytest backend/tests/test_multimodal_routes.py -v
```

### Example Test Case

```python
def test_crag_validation():
    validator = CRAGValidator()
    
    # Test validation
    context = ["The Great Wall of China was built over many centuries"]
    response = "The Great Wall was constructed in the 13th century"
    
    confidence, issues = validator.validate_facts(
        response, context, "When was the Great Wall built?"
    )
    
    assert confidence < 0.7  # Should fail (specific date not in context)
    assert len(issues) > 0
```

## Future Enhancements

1. **Multi-hop Reasoning** - Retrieve and reason across multiple documents
2. **Source Attribution** - Include citations in responses
3. **Confidence Visualization** - UI display of validation scores
4. **Knowledge Graph** - Entity-relationship based retrieval
5. **Fine-tuned Models** - Domain-specific validation models
6. **A/B Testing** - Compare CRAG vs non-CRAG responses

## Troubleshooting

### Issue: Low Confidence Scores

**Causes:**
- Insufficient context retrieval
- Generic query without specific details
- Incomplete knowledge base

**Solutions:**
- Improve vector database quality
- Provide more specific queries
- Add domain-specific documents

### Issue: Slow Response Times

**Causes:**
- Large context window (high k value)
- Model response generation delay
- Vector search inefficiency

**Solutions:**
- Reduce k value (fewer retrievals)
- Optimize FAISS index
- Use faster model (Flash vs Pro)

### Issue: Frequent Corrections

**Causes:**
- Threshold too high (0.7)
- Validation logic too strict
- Incomplete knowledge base

**Solutions:**
- Adjust confidence_threshold
- Review validation rules
- Expand knowledge base

## References

- **CRAG Paper**: [Arxiv link to CRAG implementation]
- **FAISS Documentation**: https://github.com/facebookresearch/faiss
- **Gemini API**: https://ai.google.dev/
- **RAG Best Practices**: [Internal documentation]

## Contributing

To improve CRAG implementation:

1. Test new validation rules
2. Optimize retrieval strategies
3. Enhance correction prompts
4. Monitor production metrics
5. Submit improvements via PR

---

**Last Updated:** May 13, 2026  
**Version:** 2.0  
**Status:** Production Ready
