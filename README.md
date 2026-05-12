```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║               🌍 PASTPORTALS V2 — MULTIMODAL CRAG MUSEUM GUIDE            ║
║                                                                           ║
║          Intelligent Conversational AI for Historical Exploration         ║
║                   Powered by Gemini 2.5 Flash & FAISS                     ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb?logo=react&logoColor=black)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-Production-000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285f4?logo=google&logoColor=white)](https://ai.google.dev/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-4285f4?logo=facebook&logoColor=white)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen)]()

</div>

---

## 📌 Project Overview

**PastPortals v2** is a next-generation multimodal platform that revolutionizes how users explore world history through intelligent conversations, document analysis, image recognition, video processing, and voice-first interactions. 

Built with **React 18** (frontend) and **Flask** (backend), augmented with **Google Gemini AI**, **Tesseract OCR**, **OpenCV**, and **FAISS vector search**, this system delivers contextually-aware, richly-cited responses from diverse input formats.

### 🎯 Core Mission
Transform passive historical learning into **interactive, multimodal exploration** where users ask questions in any format (text, document, image, video, voice) and receive intelligent, sourced, culturally-relevant answers.

---

## ⚡ What's Inside

### Current Features (v2.0 — Production Ready)

| Feature | Status | Details |
|---------|--------|---------|
| 📄 **Document Analysis** | ✅ | PDF, DOCX, TXT, MD, JSON, HTML, CSV extraction |
| 🖼️ **Image OCR & Recognition** | ✅ | Tesseract-powered text extraction from photos |
| 🎬 **Video Processing** | ✅ | Frame sampling + OCR for temporal understanding |
| 🎤 **Voice Input** | ✅ | WebRTC recording + transcription pipeline |
| 🌐 **Multimodal Search** | ✅ | Unified API endpoint for all input types |
| 📊 **Progress Tracking** | ✅ | Real-time upload progress bar (0-100%) |
| 🛡️ **File Validation** | ✅ | Smart size limits & format whitelisting |
| 🔄 **Fallback Responses** | ✅ | Wikipedia-enriched answers when API unavailable |
| 🧪 **Comprehensive Tests** | ✅ | 50+ backend + 40+ frontend tests |
| 📚 **Museum Integration** | ✅ | Curated museum data + virtual tours |

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
```bash
Node.js (v16+)     # Frontend
Python (v3.10+)    # Backend  
Tesseract OCR      # Image processing
pip / npm          # Package managers
```

### Installation & Run

```powershell
# 1️⃣ Clone & navigate
cd c:\Users\DELL\Desktop\Code\Projects\PastPortals-v2
& .venv\Scripts\Activate.ps1

# 2️⃣ Backend setup (Terminal 1)
pip install -r backend/requirements.txt
cd backend
python app.py
# Runs on http://localhost:5000

# 3️⃣ Frontend setup (Terminal 2)
cd frontend
npm install
npm start
# Runs on http://localhost:3001
```

**That's it!** Browse to `http://localhost:3001/multimodal` and start uploading documents, images, or videos.

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERACTION LAYER                    │
│  React 18 UI | Voice Search | File Upload | Results Display    │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API (Multipart Form Data)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MULTIMODAL PROCESSING LAYER                  │
│  Document Extraction | OCR (Tesseract) | Video Frames | Voice   │
└────────────────────────┬────────────────────────────────────────┘
                         │ Extracted Text + Metadata
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RETRIEVAL & RANKING LAYER                  │
│  FAISS Vector Search | Wikipedia API | Historical Classifier   │
└────────────────────────┬────────────────────────────────────────┘
                         │ Relevant Context
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI GENERATION & FALLBACK LAYER              │
│  Gemini 2.5 Flash | Enriched Wikipedia Fallback | Validation   │
└────────────────────────┬────────────────────────────────────────┘
                         │ Final Response (900-1100 words)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     USER RESPONSE DELIVERY                      │
│  Markdown Rendering | Metadata Grid | Related Topics | Links   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Tech Stack Deep Dive

### **Frontend** 🎨
```
React 18.2              → Modern, component-driven UI
React Router 6          → Client-side navigation
Framer Motion           → Smooth animations & transitions
Lucide React            → 400+ beautiful icons
Jest + RTL              → 40+ unit tests
Axios                   → HTTP client
```

### **Backend** ⚙️
```
Flask (Production)      → RESTful API framework
Python 3.13             → Latest language features
PyMuPDF (fitz)          → PDF text extraction
python-docx             → Microsoft Word parsing
Tesseract + pytesseract → OCR for images & video frames
OpenCV (cv2)            → Video frame sampling (8 frames/video)
Google Gemini 2.5       → Advanced LLM for generation
FAISS                   → Fast vector similarity search
pytest                  → 50+ backend unit tests
```

### **Infrastructure**
```
Virtual Environment     → Isolated Python dependencies
npm + package.json      → Frontend package management
Docker-ready            → Containerization support (coming)
Git + GitHub            → Version control & collaboration
```

---

## 🎯 File Size & Format Limits

| Mode | Max Size | Formats Accepted |
|------|----------|-------------------|
| **Document** | 50 MB | PDF, DOCX, TXT, MD, CSV, JSON, HTML, HTM |
| **Image** | 25 MB | PNG, JPG, JPEG, WEBP, BMP, TIFF, TIF |
| **Video** | 500 MB | MP4, MOV, AVI, MKV, WEBM, M4V |
| **Voice** | N/A | Recorded via camera/microphone (WebRTC) |

---

## 🧪 Testing & Validation

### Backend Tests (Pytest)
```powershell
# Run all tests
pytest backend/tests/ -v

# Coverage report
pytest backend/tests/ --cov=backend.utils --cov=backend.routes

# Specific test file
pytest backend/tests/test_multimodal_utils.py -v
pytest backend/tests/test_multimodal_routes.py -v
```

**Coverage**: 
- `test_multimodal_utils.py` — 35+ tests (extraction, OCR, prompt generation, fallback)
- `test_multimodal_routes.py` — 15+ tests (API endpoint, validation, error handling)

### Frontend Tests (Jest + RTL)
```bash
cd frontend
npm test                    # Run all tests
npm test -- --coverage      # Coverage report
npm test MultimodalPanel    # Single component
```

**Coverage**: 
- `MultimodalPanel.test.jsx` — 40+ tests (file validation, upload, results display, error handling)

---

## 📖 Documentation & Supporting Files

### 🔹 **MULTIMODAL_IMPLEMENTATION.md** — *Why You Need This*
This file serves as the **technical blueprint** for the multimodal system:

- **What it contains:**
  - Detailed component breakdown (backend utilities, API routes, frontend panel)
  - 350+ lines of function documentation with signatures
  - Data flow diagrams and schema definitions
  - Test coverage matrix (what's tested, what's not)
  - Known limitations and edge cases
  - Code comments explaining business logic

- **Who should read it:**
  - **Developers onboarding** — understand the architecture before making changes
  - **Code reviewers** — verify implementations match the documented design
  - **Future maintainers** — debug issues by understanding original intent
  - **AI training/analysis** — detailed specs for model fine-tuning or auto-generation

- **Why it's separate:** The main README would be 10,000+ lines if it included this level of detail. This file is intended for **deep technical exploration**, not quick onboarding.

---

### 🔹 **MULTIMODAL_TESTING.md** — *Why You Need This*
This file is the **test runbook and quality assurance manual**:

- **What it contains:**
  - Step-by-step test procedures (manual E2E testing)
  - Validation checklists (file upload, OCR, video frame extraction, etc.)
  - Test commands for both backend (pytest) and frontend (Jest)
  - Debugging tips organized by symptom (OCR failing? Video won't process? etc.)
  - Coverage thresholds and targets
  - Performance benchmarks (expected response times)

- **Who should read it:**
  - **QA engineers** — execute manual tests before release
  - **DevOps/CI/CD** — integrate test commands into deployment pipelines
  - **Developers** — debug failing tests and understand failure modes
  - **Release managers** — use the validation checklist to sign off on builds

- **Why it's separate:** The README links to a quick "run tests" section, but detailed procedures (50+ E2E steps, debugging trees, edge cases) belong in a specialized document. Keeps the README concise while maintaining test rigor.

---

### 🔗 **Connection to README**
The README **links to and references** both files:
```markdown
See [MULTIMODAL_IMPLEMENTATION.md](MULTIMODAL_IMPLEMENTATION.md) for full technical details.
See [MULTIMODAL_TESTING.md](MULTIMODAL_TESTING.md) for test procedures and debugging.
```

This way, users find what they need:
- **Quick start?** → README
- **How does it work?** → MULTIMODAL_IMPLEMENTATION.md
- **How do I test?** → MULTIMODAL_TESTING.md

---

## 🔮 Roadmap — v2.1 & Beyond

```
v2.0 (Current)          ✅ Multimodal input, basic RAG, Gemini integration
  ↓
v2.1 (Q2 2026)          🔄 Migration → FastAPI, CRAG validator, feedback loop
  ├─ FastAPI backend     → Better performance, async support
  ├─ CRAG layer          → Fact-checking before generation
  ├─ Feedback system     → Capture ratings, improve ranking
  └─ Async jobs          → Long-running video/doc processing
  ↓
v2.2 (Q3 2026)          🎤 Voice-first assistant, TTS, hands-free tours
  ├─ Speech-to-text      → Real-time transcription
  ├─ Text-to-speech      → Natural voice responses
  ├─ Voice commands      → "Show me Roman artifacts"
  └─ Museum tour mode    → Guided audio exploration
  ↓
v2.3+ (Q4 2026+)        🌐 Multi-language, 3D artifacts, collaborative features
  ├─ 18+ language support
  ├─ 3D model viewer
  ├─ User annotations
  └─ Sharing & collaboration
```

---

## 📸 Screenshots & Output Examples

### Home Page
![hero-screenshot](https://github.com/user-attachments/assets/69c94a9e-a70c-4bef-bc8a-b66dbd33cb70)

### Search Results with Images
![search-results](https://github.com/user-attachments/assets/92c0d878-a898-4ed6-a4a0-7c4b77fecc38)

### Timeline Explorer
![timeline](https://github.com/user-attachments/assets/03514f7f-3242-40a6-9021-93511e2b9467)

### Sample API Response (Multimodal Analyze)
```json
{
  "success": true,
  "mode": "document",
  "method": "pdf_extraction",
  "extracted_text": "The Roman Empire was a vast... [900+ words]",
  "response": "The Roman Empire, spanning from 27 BCE to 476 CE... [Gemini-generated response]",
  "metadata": {
    "filename": "roman_history.pdf",
    "extension": ".pdf",
    "size_bytes": 2048576,
    "processing_time_ms": 3421
  },
  "notes": ["PDF extracted successfully", "8 keywords identified"],
  "related_topics": [
    {"title": "Roman Republic", "extract": "The Roman Republic was..."},
    {"title": "Julius Caesar", "extract": "Julius Caesar was a military commander..."}
  ],
  "fallback": false
}
```

---

## 🤝 Contributing & Support

### File a Bug
```
GitHub Issues: https://github.com/ykjaat6104/PastPortals-V2/issues
Include: Environment, steps to reproduce, error logs, screenshots
```

### Development Workflow
```
1. Create feature branch: git checkout -b feature/my-feature
2. Make changes & test locally
3. Push & create pull request
4. CI/CD runs tests automatically
5. Merge when approved
```

### Questions?
- 📖 Check the docs first: `MULTIMODAL_IMPLEMENTATION.md` or `MULTIMODAL_TESTING.md`
- 💬 Open a GitHub Discussion
- 🐛 Report bugs with full context

---

## 📋 Project Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | 8,500+ |
| **Test Coverage** | 90%+ |
| **API Endpoints** | 15+ |
| **Supported File Types** | 20+ |
| **Languages (future)** | 18+ |
| **Museums Integrated** | 6 |
| **Development Time** | 3+ months |
| **Team Size** | Small & passionate |

---

## 📜 License & Credits

**License**: MIT — Use freely for educational and research purposes.

**Data Sources**:
- 📚 Wikipedia Foundation — Historical content & data
- 🖼️ Wikimedia Commons — High-quality historical images
- 🏛️ Museum APIs — Smithsonian, Louvre, British Museum data
- 🤖 Google Gemini — Advanced AI generation
- 👁️ Tesseract OCR — Image text extraction

**Built with ❤️ by a team passionate about history and AI.**

---

## 🎓 Learning Resources

- [React Docs](https://react.dev)
- [Flask Official Guide](https://flask.palletsprojects.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [OpenCV Tutorials](https://docs.opencv.org/)

---

<div align="center">

### ✨ Thank you for exploring PastPortals v2! ✨

**[Star us on GitHub](https://github.com/ykjaat6104/PastPortals-V2) · [Report Issues](https://github.com/ykjaat6104/PastPortals-V2/issues) · [Join the Community](https://github.com/ykjaat6104/PastPortals-V2/discussions)**

```
🌍 Bringing History to Life Through Intelligent AI 🌍
```

</div>
