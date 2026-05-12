# PastPortals v2: AI-Powered Multimodal CRAG System for Cultural Heritage Interpretation

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285f4)](https://ai.google.dev/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Database-4285f4)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Project Overview

PastPortals is an intelligent, AI-powered museum guide system developed as a response to limitations in traditional and existing digital museum information systems. The platform integrates **Correction + Retrieval-Augmented Generation (CRAG)**, natural language processing, multimodal interaction, vector-based retrieval, voice-first conversational AI, and continuous self-improving feedback loops to deliver accurate, context-aware, and engaging cultural heritage experiences.

---

## Problem Statement & Motivation

### Limitations of Existing Systems

Traditional museum systems rely on static methods—printed labels, brochures, audio guides—that fail to:
- Provide interactive or personalized visitor experiences
- Address diverse visitor questions and interests in depth
- Support context-aware, domain-specific explanations

Conversely, LLM-based conversational systems suffer from:
- **Hallucination**: Generation of inaccurate or unsupported information
- **Lack of domain grounding**: Insufficient knowledge of historical and cultural contexts
- **No transparency**: Inability to verify information sources
- **Limited multimodal support**: Restricted to single interaction modes
- **Poor scalability**: Inefficient handling of simultaneous visitors

### Proposed Solution

PastPortals implements **Correction + Retrieval-Augmented Generation (CRAG)** to bridge this gap by:
1. Retrieving verified information from curated knowledge bases
2. Validating and correcting generated content through fact-checking mechanisms
3. Supporting multimodal interaction (text, voice, image, video)
4. Enabling voice-first conversational AI for hands-free cultural exploration
5. Implementing intelligent feedback loops that refine system behavior with each user interaction
6. Enabling multilingual communication across 18+ languages
7. Ensuring scalability and continuous improvement for high-traffic museum environments

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Frontend Application Layer                    │
│              React 18 | Document Upload | Voice Interface           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST API
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Content Processing Layer                        │
│        Document Extraction | OCR | Video Analysis | Voice           │
│        (PyMuPDF | python-docx | Tesseract | OpenCV)                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Extracted Content + Metadata
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Retrieval & Ranking Layer                         │
│              FAISS Vector Search | Wikipedia API                    │
│              Historical Content Classification                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Contextually Relevant Information
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Generation & Response Layer                        │
│        Google Gemini 2.5 Flash | Fallback Enrichment               │
│              Fact Validation | Response Synthesis                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Generated Response with Metadata
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Response Delivery Layer                          │
│         Markdown Rendering | Audio Output | Related Topics          │
└─────────────────────────────────────────────────────────────────────┘
```

### System Architecture Visualization

![Component Hierarchy - System Architecture Layers](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/component_hierarchy.png)

### Technology Stack

![Technology Stack v2 - Multimodal CRAG System](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/tech_stack_architecture.png)

#### **Frontend Architecture** 🎨
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **UI Framework** | React 18.2 | Component-based interface with virtual DOM rendering |
| **Routing** | React Router 6 | Client-side navigation and state management |
| **Animations** | Framer Motion | Smooth transitions and interactive UI elements |
| **Icons** | Lucide React | Comprehensive, accessible icon system |
| **HTTP Client** | Axios | RESTful API communication with request/response interceptors |
| **Testing** | Jest + React Testing Library | 40+ component tests with coverage reporting |

#### **Backend Infrastructure** ⚙️
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI | High-performance async REST API framework |
| **Language** | Python 3.13 | Primary backend language with modern features |
| **Async Processing** | asyncio + uvicorn | Non-blocking concurrent request handling |
| **Testing** | pytest | 50+ unit tests with comprehensive coverage |
| **API Documentation** | Pydantic + Swagger | Auto-generated interactive API documentation |

#### **Content Processing & Extraction** 📄
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **PDF Extraction** | PyMuPDF (fitz) | High-fidelity text and metadata extraction |
| **Word Documents** | python-docx | Structured parsing of DOCX format |
| **Optical Character Recognition** | pytesseract + Tesseract | Text extraction from images and scanned documents |
| **Video Analysis** | OpenCV (cv2) | Frame sampling and temporal processing (8 frames/video) |
| **Voice Processing** | Web Speech API | Real-time speech-to-text transcription |

#### **AI/ML & Generation Layer** 🧠
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM Generation** | Google Gemini 2.5 Flash | Advanced language generation with low latency |
| **Retrieval-Augmented** | CRAG (Correction Module) | Fact validation and hallucination correction |
| **Vector Similarity** | FAISS | Fast approximate nearest neighbor search |
| **Sentence Embeddings** | Sentence Transformers | Dense vector representation of content |
| **Domain Classification** | Historical Keyword Analysis | Context-aware content categorization |

#### **Voice-First Conversational AI** 🎙️
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Speech-to-Text** | Google Cloud Speech-to-Text / Web Speech API | Multilingual voice input processing |
| **Natural Language Understanding** | LLM + RAG Pipeline | Intent extraction and query comprehension |
| **Text-to-Speech** | Google Cloud Text-to-Speech | Natural-sounding response delivery |
| **Voice Assistant Framework** | Custom voice conversation bot | Context-aware dialogue management |
| **Real-time Streaming** | WebSocket support | Continuous voice interaction without latency |

#### **Data & Retrieval Systems** 📚
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Vector Database** | FAISS with in-memory indexing | Millisecond-level similarity search |
| **Knowledge Bases** | Wikipedia API + Smithsonian Open Access | Curated historical content retrieval |
| **Domain Datasets** | Custom museum collections | Institution-specific artifact metadata |
| **Feedback Storage** | JSON + structured logs | User interaction tracking for improvement |
| **Cache Layer** | Redis (optional) | Response caching and session management |

#### **Intelligent Feedback Loop System** 🔄
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **User Interaction Tracking** | Event logging pipeline | Capture queries, dwell time, user ratings |
| **Feedback Collection** | Implicit + explicit signals | Track relevance, accuracy, and satisfaction |
| **Vector Similarity Refinement** | Weight adjustment algorithms | Dynamically tune ranking for domain-specific queries |
| **Model Adaptation** | Online learning mechanisms | Continuous improvement of retrieval quality |
| **Performance Monitoring** | Metrics & analytics dashboard | Track system improvement across sessions |

---
## System Objectives

The development of PastPortals targets the following key objectives:

1. **Accuracy & Reliability**: Ground all responses in trusted, curated datasets with fact-checking mechanisms to reduce hallucination and enhance credibility
2. **Voice-First Interaction**: Enable seamless voice-based conversational interfaces for hands-free cultural exploration with natural language understanding
3. **Continuous Self-Improvement**: Implement intelligent feedback loops that refine retrieval ranking, response quality, and domain understanding from every user interaction
4. **Multilingual Support**: Provide accessibility across 18+ languages for diverse visitor populations with cultural context preservation
5. **Multimodal Delivery**: Process and respond to diverse input modalities (text, voice, image, video) while delivering content in preferred formats
6. **Scalability & Performance**: Handle multiple concurrent users without degradation using FastAPI async architecture
7. **Accessibility & Cultural Sensitivity**: Maintain authenticity in heritage interpretation while supporting diverse learning styles and accessibility requirements

---

## Core Features

### Current Implementation (v2.0)

| Feature | Implementation |
|---------|-----------------|
| Document Processing | PDF, DOCX, TXT, MD, JSON, CSV, HTML extraction |
| Image Recognition | Tesseract-based OCR for photographic content |
| Video Analysis | Frame sampling with temporal OCR processing |
| Voice Interaction | WebRTC recording + transcription pipeline |
| Unified API | Single endpoint supporting all input modalities |
| Progress Tracking | Real-time upload status visualization (0-100%) |
| Content Validation | Format and size limit enforcement with user feedback |
| Fallback Responses | Wikipedia-enriched responses for API unavailability |
| Comprehensive Testing | 50+ backend + 40+ frontend unit tests |
| Museum Integration | Curated museum data and virtual tour content |

### File Processing Specifications

| Category | Maximum Size | Supported Formats |
|----------|--------------|-------------------|
| Documents | 50 MB | PDF, DOCX, TXT, MD, CSV, JSON, HTML, HTM |
| Images | 25 MB | PNG, JPG, JPEG, WEBP, BMP, TIFF, TIF |
| Video | 500 MB | MP4, MOV, AVI, MKV, WEBM, M4V |
| Voice | N/A | Real-time recording via WebRTC |

---

## Intelligent Self-Improving Feedback Loop System

![Self-Improving Intelligence - The Feedback Loop](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/feedback_loop_system.png)

Every user interaction represents an opportunity for system learning. PastPortals v2 incorporates a sophisticated feedback pipeline that continuously refines retrieval accuracy, response relevance, and domain understanding.

### Feedback Mechanism Architecture

**Stage 1: User Feedback Captured**
- Explicit ratings and implicit signals (re-queries, dwell time) logged per interaction
- Domain context stored with each query-response pair
- User satisfaction metrics tracked across museum exhibition types

**Stage 2: Ranking Model Updated**  
- Feedback dynamically adjusts vector similarity weights
- Domain classifier confidence thresholds refined based on user validation
- Historical accuracy data incorporated into retrieval ranking

**Stage 3: System Evolution**
- Pipeline gets measurably smarter with each user session
- Adaptive behavior emerges from aggregated feedback signals
- Cultural context understanding deepens through continuous learning

### Key Benefits

- **Adaptive Responses**: Museum guides learn visitor preferences and knowledge levels
- **Domain Refinement**: Historical accuracy improves through expert feedback integration
- **Personalization**: Interaction quality increases for returning visitors
- **Continuous Validation**: User corrections automatically retrain ranking models

---

## Voice-First Conversational AI Bot

![Voice-First Conversational AI](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/voice_ai_architecture.png)

PastPortals v2 delivers a seamless, hands-free cultural exploration experience through intelligent voice-first conversational AI.

### Core Voice Features

| Feature | Technology | Implementation |
|---------|-----------|-----------------|
| **Speech-to-Text Input** | Google Cloud Speech-to-Text / Web Speech API | Converts user voice into text queries in real-time |
| **AI Understanding** | LLM + RAG + CRAG Pipeline | Processes natural language intent with cultural context |
| **Text-to-Speech Output** | Google Cloud Text-to-Speech | Delivers responses as natural, human-like voice |
| **Real-Time Interaction** | WebSocket streaming protocol | Instant conversational feedback without latency |
| **Context-Aware Dialogue** | Domain-aware conversation state | Adapts responses based on museum location and artifact |
| **Multilingual Support** | 18+ language voice processing | Bilingual interactions for international visitors |

### Use Case: Bilingual Voice Interaction

A visitor asks in English about an ancient artifact. The system:
1. Captures voice query in real-time
2. Understands cultural/historical context
3. Retrieves verified artifact information via CRAG pipeline
4. Delivers response in visitor's native language via text-to-speech
5. Captures feedback for future refinement

### Technical Stack for Voice AI

- **Voice Input**: Web Speech API + Whisper transcription
- **Voice Processing**: TensorFlow Lite for on-device optimization
- **Response Generation**: Gemini 2.5 Flash with domain context
- **Voice Output**: Google Cloud TTS with natural prosody
- **Conversation Management**: State machine for dialogue flow

---

## Data Flow: Multimodal Intelligent Pipeline

![Data Flow - Multimodal Intelligent Pipeline](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/data_flow_pipeline.png)

PastPortals v2 represents a complete data journey, from diverse user inputs to intelligent, verified outputs, constantly refining itself through feedback.

### Processing Pipeline

1. **User Input Acquisition** → Text, Voice, Image, or Video submission
2. **Multimodal Processing** → Speech-to-Text, OCR, Frame Extraction, Document Parsing
3. **Domain Classification** → Historical/cultural context detection
4. **Vector Retrieval** → FAISS semantic search of curated knowledge bases
5. **LLM Generation** → Google Gemini 2.5 Flash response synthesis
6. **Fact Validation** → CRAG correction module validates accuracy
7. **Output Delivery** → Markdown-formatted response + voice synthesis
8. **Feedback Collection** → User interaction logged for continuous improvement
9. **System Refinement** → Ranking and understanding models updated

---

### System Requirements

- **Node.js**: v16 or higher
- **Python**: v3.10 or higher
- **Tesseract OCR**: System-level installation required
- **Virtual Environment**: Python venv or equivalent

### Development Setup

```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Configure environment variables
# Root .env file:
# GEMINI_API_KEY=your_api_key
# CORS_ORIGINS=http://localhost:3001

# frontend/.env file:
# PORT=3001
# REACT_APP_API_URL=http://localhost:5000
```

### Running the Application

**Terminal 1 - Backend Server:**
```powershell
cd backend
# FastAPI server (async support for concurrent requests)
uvicorn app:app --reload --port 5000

# Or using Python directly (if configured)
python app.py
# Server runs on http://localhost:5000 with auto-generated docs at http://localhost:5000/docs
```

**Terminal 2 - Frontend Application:**
```bash
cd frontend
npm start
# Application accessible at http://localhost:3001
```

Navigate to `http://localhost:3001/multimodal` to access the multimodal input interface.

---

## Production Deployment Architecture

![Deployment Architecture - Multi-Tier Production Environment](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/deployment_architecture.png)

---

## Testing & Quality Assurance

### Backend Testing

```powershell
# Execute all backend tests
pytest backend/tests/ -v

# Generate coverage report
pytest backend/tests/ --cov=backend.utils --cov=backend.routes --cov-report=html

# Test specific modules
pytest backend/tests/test_multimodal_utils.py -v
pytest backend/tests/test_multimodal_routes.py -v
```

**Test Coverage**: 
- `test_multimodal_utils.py`: 35+ tests (content extraction, OCR validation, response generation)
- `test_multimodal_routes.py`: 15+ tests (API endpoint validation, error handling)
- **Aggregate Coverage**: 90%+ of core functionality

### Frontend Testing

```bash
cd frontend
npm test                    # Execute all component tests
npm test -- --coverage      # Generate coverage report
npm test MultimodalPanel    # Test specific component
```

**Test Coverage**:
- `MultimodalPanel.test.jsx`: 40+ tests (file validation, upload workflow, results display)
- **Framework**: Jest + React Testing Library

---

## API Specification

### Primary Endpoint: Multimodal Analysis

**Endpoint**: `POST /api/multimodal/analyze`

**Request Format**:
```
Content-Type: multipart/form-data

Parameters:
- file (optional): File object (document/image/video)
- question (required): User query string
- mode (required): Input modality (document|image|video|voice)
```

**Response Schema**:
```json
{
  "success": boolean,
  "mode": "document|image|video|voice",
  "method": "text-file|pdf|docx|ocr-image|ocr-video|generic-text",
  "extracted_text": "Full text extracted from input",
  "response": "Generated or fallback response (900-1100 words)",
  "metadata": {
    "filename": "original_filename.ext",
    "extension": ".pdf|.jpg|.mp4|...",
    "size_bytes": number,
    "processing_method": "extraction_method_used"
  },
  "notes": ["Processing note 1", "Processing note 2"],
  "related_topics": [
    {
      "title": "Topic Title",
      "extract": "Brief description from Wikipedia"
    }
  ],
  "fallback": false
}
```

---

## Documentation

This repository includes comprehensive technical documentation:

### MULTIMODAL_IMPLEMENTATION.md
Detailed technical specifications including:
- Component architecture and function signatures
- Data extraction methodologies (PDF, DOCX, OCR, video processing)
- Response generation and fallback mechanisms
- Database schema and metadata structures
- Test coverage matrices and known limitations

**Intended Audience**: Developers, code maintainers, technical architects

### MULTIMODAL_TESTING.md
Comprehensive testing procedures including:
- Unit test execution commands and validation checklists
- End-to-end testing procedures for each input modality
- Debugging trees organized by symptom/failure mode
- Performance benchmarks and acceptance criteria
- Continuous integration recommendations

**Intended Audience**: QA engineers, DevOps professionals, deployment teams

---

## Roadmap & Future Development

### Version 2.0 (Current Release)
✅ **CRAG (Correction + RAG)**: Fact-checking module for hallucination prevention  
✅ **Voice-First Conversational AI**: Hands-free interaction with natural language understanding  
✅ **Intelligent Feedback Loop**: Self-improving system that learns from user interactions  
✅ **FastAPI Backend**: Async architecture for improved scalability and performance  
✅ **Multimodal Processing**: Support for documents, images, videos, and voice input  

### Version 2.1 (Planned - Q2 2026)
- **Enhanced CRAG Validator**: Multi-stage fact verification with source attribution
- **Feedback-Driven Ranking**: Advanced machine learning for personalized retrieval
- **Asynchronous Job Processing**: Handle large document/video files without blocking
- **Knowledge Graph Integration**: Semantic relationship mapping for cultural artifacts
- **Performance Optimization**: Latency reduction to <500ms for voice interactions

### Version 2.2 (Planned - Q3 2026)
- **Expanded Voice Features**: Speaker identification and conversation context memory
- **Multilingual Enhancement**: Full 18+ language support with cultural context preservation
- **Mobile Voice Assistant**: Dedicated mobile app with voice-first experience
- **Real-time Collaboration**: Multiple visitors discussing same artifact with shared feedback

### Version 2.3+ (Planned - Q4 2026+)
- **3D Artifact Visualization**: Interactive 3D models of museum pieces with voice guidance
- **Augmented Reality Integration**: AR overlays powered by voice commands
- **Collaborative Annotation**: Visitor annotations that improve cultural understanding
- **Institutional Dashboard**: Museum analytics tracking visitor learning and engagement

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Lines of Code | 8,500+ |
| Test Coverage | 90%+ |
| API Endpoints | 15+ |
| Supported File Types | 20+ |
| Supported Languages | 18+ (planned) |
| Museum Partnerships | 6 institutions |
| Development Duration | 3+ months |

![Project Statistics & Metrics](https://raw.githubusercontent.com/ykjaat6104/PastPortals-V2/main/diagrams/project_statistics.png)

---

## Key References & Data Sources

- **Content**: Wikipedia Foundation (en.wikipedia.org)
- **Historical Images**: Wikimedia Commons
- **Museum Data**: Smithsonian Open Access, Louvre API, British Museum Collections
- **AI Generation**: Google Generative AI (Gemini 2.5 Flash)
- **OCR Engine**: Tesseract Open Source OCR
- **Vector Search**: Facebook FAISS
- **Video Processing**: OpenCV Foundation

---

## Contributing & Support

### Reporting Issues
Please submit issues via GitHub Issues with:
- Detailed description and reproduction steps
- Environment specifications (OS, Python version, Node version)
- Error logs and stack traces
- Screenshots or relevant attachments

### Development Workflow
1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement changes and execute tests locally
3. Commit with descriptive messages following conventional commits
4. Push to remote and create pull request
5. Submit for code review and CI/CD validation

### Technical Support
- Documentation: See [MULTIMODAL_IMPLEMENTATION.md](MULTIMODAL_IMPLEMENTATION.md) and [MULTIMODAL_TESTING.md](MULTIMODAL_TESTING.md)
- GitHub Discussions: Community Q&A and feature discussion
- Issue Tracker: Bug reports and feature requests

---

## Sample Output

### Multimodal Analysis Result

```json
{
  "success": true,
  "mode": "document",
  "method": "pdf_extraction",
  "extracted_text": "The Roman Empire was one of the most influential civilizations in human history, spanning over 500 years...",
  "response": "The Roman Empire, originating from the Italian peninsula, became a dominant force that transformed Western civilization. From 27 BCE to 476 CE, Rome developed sophisticated administrative systems, advanced architectural techniques, and influential legal frameworks. Key achievements include the construction of infrastructure such as aqueducts, roads, and amphitheaters, alongside the development of Latin as a universal language. The Roman military was renowned for its organization and effectiveness, while Roman law established principles that continue to influence modern legal systems.",
  "metadata": {
    "filename": "roman_history.pdf",
    "extension": ".pdf",
    "size_bytes": 2048576,
    "processing_method": "pdf_extraction"
  },
  "notes": [
    "PDF extracted successfully with 8 keywords identified",
    "Content grounded in Wikipedia historical data"
  ],
  "related_topics": [
    {
      "title": "Roman Republic",
      "extract": "The Roman Republic was the period of Roman history when the state operated as a republic..."
    },
    {
      "title": "Julius Caesar",
      "extract": "Gaius Julius Caesar was a Roman military general and statesman who played a critical role..."
    }
  ],
  "fallback": false
}
```

### User Interface Examples

**Document Upload Interface**
![Hero Screenshot](https://github.com/user-attachments/assets/69c94a9e-a70c-4bef-bc8a-b66dbd33cb70)

**Search Results with Historical Context**
![Search Results](https://github.com/user-attachments/assets/92c0d878-a898-4ed6-a4a0-7c4b77fecc38)

**Timeline Navigation**
![Timeline View](https://github.com/user-attachments/assets/03514f7f-3242-40a6-9021-93511e2b9467)

---

## License & Attribution

This project is distributed under the **MIT License** for educational and research purposes.

**Data Attribution**:
- Historical Content: Wikipedia Foundation
- Imagery: Wikimedia Commons (Creative Commons License)
- Museum Information: Official institutional APIs
- AI Capabilities: Google Gemini API
- OCR Technology: Tesseract OCR Project

---

## Authors

**Project Team**:
- Manu Awasthi (2204920100079)
- Pushkar Raj Vats (2204920100116)
- Satendra Kumar (2204920100141)
- Sunny Raj (2204920100164)
- Yash Kumar Kalirawan (2204920100183)

**Faculty Advisor**: Dr. Balak Ram  
**Institution**: KCC Institute of Technology and Management  
**University**: Dr. A.P.J. Abdul Kalam Technical University, Lucknow

---

## Keywords

Artificial Intelligence · Museums · Conversational Agents · Retrieval-Augmented Generation · Multimodal AI · Visitor Engagement · Cultural Heritage · Natural Language Processing · Vector Databases · OCR Technology

---

**PastPortals v2** — Advancing Cultural Heritage Interpretation Through Intelligent Technology
