# PastPortals v2: AI-Powered Multimodal RAG-Based Approach for Cultural Heritage Interpretation

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb?logo=react&logoColor=black)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-Production-000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285f4)](https://ai.google.dev/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Database-4285f4)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Project Overview

PastPortals is an intelligent, AI-powered museum guide system developed as a response to limitations in traditional and existing digital museum information systems. The platform integrates Retrieval-Augmented Generation (RAG), natural language processing, multimodal interaction, and vector-based retrieval to deliver accurate, context-aware, and engaging cultural heritage experiences.

### Executive Summary

This project addresses critical challenges in museum information delivery by combining advanced technologies—Large Language Models (LLMs), FAISS vector search, speech processing, and multimodal interfaces—within a Retrieval-Augmented Generation framework. The system eliminates hallucination risks inherent to pure LLM-based approaches by grounding all responses in curated, verified knowledge bases.

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

PastPortals implements **Retrieval-Augmented Generation (RAG)** to bridge this gap by:
1. Retrieving verified information from curated knowledge bases
2. Generating responses grounded in reliable sources
3. Supporting multimodal interaction (text, voice, visual)
4. Enabling multilingual communication
5. Ensuring scalability for high-traffic museum environments

---

## System Objectives

The development of PastPortals targets the following key objectives:

1. **Accuracy & Reliability**: Ground all responses in trusted, curated datasets to reduce hallucination and enhance credibility
2. **Natural Interaction**: Enable conversational interfaces supporting both text and voice input
3. **Multilingual Support**: Provide accessibility across 18+ languages for diverse visitor populations
4. **Multimodal Delivery**: Combine text, audio, and visual outputs to cater to different learning preferences
5. **Scalability**: Handle multiple concurrent users without performance degradation
6. **Cultural Sensitivity**: Maintain authenticity and accuracy in heritage interpretation
7. **Accessibility**: Support diverse learning styles and accessibility requirements

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

### Technology Stack

#### Frontend
- **React 18.2**: Component-based user interface framework
- **React Router 6**: Client-side application routing
- **Framer Motion**: Animation and transition effects
- **Lucide React**: Comprehensive icon library
- **Jest & React Testing Library**: Component unit testing
- **Axios**: HTTP client for API communication

#### Backend
- **Flask**: Lightweight RESTful API framework
- **Python 3.13**: Primary backend language
- **PyMuPDF (fitz)**: PDF text extraction and analysis
- **python-docx**: Microsoft Word document processing
- **pytesseract**: Optical Character Recognition (OCR)
- **OpenCV (cv2)**: Video frame sampling and analysis (8 frames per video)
- **Google Gemini 2.5 Flash**: Advanced language model for generation
- **FAISS**: Fast similarity search and vector indexing
- **pytest**: Backend unit testing framework
- **Wikipedia API**: Historical content retrieval

---

## Core Features

### Current Implementation (v2.0)

| Feature | Status | Implementation |
|---------|--------|-----------------|
| Document Processing | ✓ Implemented | PDF, DOCX, TXT, MD, JSON, CSV, HTML extraction |
| Image Recognition | ✓ Implemented | Tesseract-based OCR for photographic content |
| Video Analysis | ✓ Implemented | Frame sampling with temporal OCR processing |
| Voice Interaction | ✓ Implemented | WebRTC recording + transcription pipeline |
| Unified API | ✓ Implemented | Single endpoint supporting all input modalities |
| Progress Tracking | ✓ Implemented | Real-time upload status visualization (0-100%) |
| Content Validation | ✓ Implemented | Format and size limit enforcement with user feedback |
| Fallback Responses | ✓ Implemented | Wikipedia-enriched responses for API unavailability |
| Comprehensive Testing | ✓ Implemented | 50+ backend + 40+ frontend unit tests |
| Museum Integration | ✓ Implemented | Curated museum data and virtual tour content |

### File Processing Specifications

| Category | Maximum Size | Supported Formats |
|----------|--------------|-------------------|
| Documents | 50 MB | PDF, DOCX, TXT, MD, CSV, JSON, HTML, HTM |
| Images | 25 MB | PNG, JPG, JPEG, WEBP, BMP, TIFF, TIF |
| Video | 500 MB | MP4, MOV, AVI, MKV, WEBM, M4V |
| Voice | N/A | Real-time recording via WebRTC |

---

## Installation & Deployment

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
python app.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend Application:**
```bash
cd frontend
npm start
# Application accessible at http://localhost:3001
```

Navigate to `http://localhost:3001/multimodal` to access the multimodal input interface.

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

### Version 2.1 (Planned - Q2 2026)
- Migration from Flask to **FastAPI** framework for improved async performance
- Implementation of **CRAG (Correction + RAG)** validator layer
- Development of intelligent feedback loop system
- Asynchronous job processing for large document/video files

### Version 2.2 (Planned - Q3 2026)
- Voice-first conversational assistant with natural language understanding
- Real-time speech-to-text integration
- Text-to-speech response delivery
- Voice-controlled navigation and actions

### Version 2.3+ (Planned - Q4 2026+)
- Expanded multilingual support (18+ languages)
- 3D artifact visualization and exploration
- Collaborative features and user annotation capabilities
- Docker and Kubernetes deployment manifests

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
