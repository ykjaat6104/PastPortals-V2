# 🌍 PastPortals v2 - Your Gateway to World History

**PastPortals v2** is an advanced AI-powered multimodal platform that brings world history to life through intelligent conversations, document analysis, image recognition, video processing, voice input, real historical images, and interactive museum guides. Built with React and Flask, powered by Google Gemini 2.5 Flash, it provides an immersive journey through time and civilizations with support for multiple content formats.


<img width="1920" height="1080" alt="Screenshot (71)" src="https://github.com/user-attachments/assets/69c94a9e-a70c-4bef-bc8a-b66dbd33cb70" />


## ✨ Key Features

### 🚀 **Multimodal Content Analysis (NEW in v2)**
- **Document Upload**: Extract and analyze PDF, DOCX, TXT, MD, CSV, JSON, HTML files
- **Image Recognition**: OCR-powered analysis of historical photographs and documents
- **Video Processing**: Automatic frame sampling and text extraction from video content
- **Voice Input**: Record and transcribe voice queries for hands-free interaction
- **File Validation**: Real-time validation with size limits (50MB docs, 25MB images, 500MB videos)
- **Upload Progress**: Visual progress bar with percentage tracking
- **Content Preview**: Image thumbnails, video player, and file metadata display

### 🤖 **AI-Powered Historical Analysis**
- Intelligent analysis of documents, images, and video content
- Powered by Google Gemini 2.5 Flash for accurate, comprehensive responses
- Context-aware answers with minimum 500+ word detailed explanations
- Automatic fallback to enriched Wikipedia responses when API quotas reached
- Metadata extraction (file info, processing method, extracted text, related topics)

### 🖼️ **Real Historical Images**
- Automatic image sourcing from Wikimedia Commons
- Wikipedia-style text wrapping layout with authentic historical photographs
- 3-4 curated images per topic with source attribution
- Professional grid layout optimized for reading

### 🌐 **Multi-Language Translation**
- Real-time translation to 18+ languages
- Support for: English, Hindi, French, Spanish, Portuguese, Arabic, Chinese, Japanese, German, Italian, Russian, Korean, and more
- Seamless language switching without page reload

### 🎤 **Voice Search Integration**
- Hands-free search using Web Speech API
- Visual feedback with color-coded status (Red: listening, Blue: ready)
- Works in Chrome, Edge, and Brave browsers
- Green search button for manual queries
- Voice recording for multimodal video input

### 🏛️ **Interactive Museum Explorer**
- Virtual tours of world-famous museums
- Featured institutions: Louvre, British Museum, National Museum India, Egyptian Museum, Smithsonian, Palace Museum
- Direct links to official museum websites
- Detailed highlights and establishment history

### 📜 **Historical Timeline Navigation**
- Explore major historical periods and events
- Interactive timeline with categorized eras
- Quick-access topic tags for popular searches

### 🔍 **Smart Search System**
- Wikipedia-powered search with AI enhancement
- Auto-search from topic tags and suggestions
- Search available on all pages including multimodal explorer
- Instant results with comprehensive explanations

### 📊 **Professional UI/UX**
- Clean, modern design with light theme
- Elegant sidebar navigation
- Responsive layout for mobile, tablet, and desktop
- Smooth animations and hover effects
- Professional typography and spacing

<img width="1920" height="1080" alt="Screenshot (72)" src="https://github.com/user-attachments/assets/92c0d878-a898-4ed6-a4a0-7c4b77fecc38" />


<img width="1920" height="1080" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/03514f7f-3242-40a6-9021-93511e2b9467" />


## 🎯 Use Cases

- **Students & Educators**: Research historical topics with verified sources
- **History Enthusiasts**: Deep dive into civilizations, wars, and cultural movements
- **Museum Visitors**: Pre-visit research and virtual museum exploration
- **Language Learners**: Study history in multiple languages
- **Content Creators**: Gather accurate historical information with citations

---

## 🏗️ Technical Architecture

### **Frontend Stack**
- **Framework**: React 18.2.0
- **Routing**: React Router DOM 6.20.1
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Styling**: Custom CSS with CSS Variables
- **API Integration**: Fetch API with async/await
- **Testing**: Jest & React Testing Library

### **Backend Stack**
- **Framework**: Flask (Python 3.13)
- **AI Model**: Google Gemini 2.5 Flash
- **Content Extraction**: PyMuPDF, python-docx, pdfplumber, Tesseract OCR
- **Video Processing**: OpenCV (cv2)
- **APIs**: Wikipedia API, Wikimedia Commons API
- **CORS**: Flask-CORS for cross-origin requests
- **Vector Database**: FAISS
- **Testing**: pytest with 50+ test cases 

### **Project Structure**
```
PastPortals-v2/
├── frontend/                    # React Application
│   ├── public/
│   │   └── index.html          # HTML template
│   ├── src/
│   │   ├── components/         # React Components
│   │   │   ├── Home.jsx        # Landing page
│   │   │   ├── SearchPageNew.jsx      # Main search interface
│   │   │   ├── TimelinePageNew.jsx    # Timeline explorer
│   │   │   ├── MuseumsPageNew.jsx     # Museum directory
│   │   │   ├── MultimodalPanel.jsx    # Unified multimodal input (NEW)
│   │   │   ├── MultimodalPanel.test.jsx # Component tests (NEW)
│   │   │   ├── VoiceSearchBar.jsx     # Voice search component
│   │   │   ├── Header.jsx      # Navigation header
│   │   │   └── Sidebar.jsx     # Navigation sidebar
│   │   ├── contexts/           # React Context
│   │   │   ├── APIContext.jsx  # API state management
│   │   │   └── NotificationContext.jsx
│   │   ├── styles/             # CSS Styling
│   │   │   ├── globals.css     # Global styles
│   │   │   ├── components.css  # Component & multimodal styles
│   │   │   └── sidebar.css     # Sidebar styles
│   │   ├── utils/              # Utilities
│   │   │   ├── api.js          # API functions
│   │   │   └── imageSearch.js  # Wikimedia image fetcher
│   │   ├── App.jsx             # Main app component
│   │   └── index.js            # Entry point
│   ├── .env                    # Frontend config (PORT=3001)
│   └── package.json            # Dependencies
│
├── backend/                    # Flask API Server
│   ├── app.py                  # Main Flask app
│   ├── config.py               # Configuration
│   ├── routes/                 # API Routes
│   │   ├── qa_routes.py        # Q&A endpoints
│   │   ├── multimodal_routes.py # Multimodal analysis (NEW)
│   │   ├── translate_routes.py # Translation
│   │   ├── summarize_routes.py # Summarization
│   │   ├── museum_routes.py    # Museum data
│   │   └── config_routes.py    # Config endpoints
│   ├── utils/                  # Backend utilities
│   │   ├── ai_utils.py         # Gemini AI integration
│   │   ├── multimodal_utils.py # File extraction & analysis (NEW)
│   │   ├── wikipedia_utils.py  # Wikipedia API
│   │   ├── museum_utils.py     # Museum data
│   │   ├── vector_utils.py     # Vector operations
│   │   └── history_utils.py    # History utilities
│   ├── tests/                  # Test Suite (NEW)
│   │   ├── test_multimodal_utils.py   # Backend utility tests
│   │   └── test_multimodal_routes.py  # API endpoint tests
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Virtual environment
│
├── .env                        # Environment variables (API keys)
├── MULTIMODAL_IMPLEMENTATION.md # v2 feature documentation (NEW)
├── MULTIMODAL_TESTING.md       # Testing guide & procedures (NEW)
├── SETUP.md                    # Installation guide
├── ARCHITECTURE.md             # Architecture documentation
├── README.md                   # This file
└── package.json                # Root dependencies
```

---

## 🚀 Quick Start Guide

### **Prerequisites**

Before running PastPortals v2, ensure you have:

1. **Node.js** (v16 or higher)
   - Download: https://nodejs.org
   - Verify: `node --version`

2. **Python** (v3.10 or higher)
   - Download: https://python.org
   - Verify: `python --version`

3. **Google Gemini API Key**
   - Get free key: https://aistudio.google.com/app/apikey
   - Required for AI features

4. **Tesseract OCR** (for image/video text extraction)
   - Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

### **Installation Steps**

#### **Quick Setup**

```bash
# 1. Navigate to project
cd "C:\Users\DELL\Desktop\Code\Projects\PastPortals-v2"

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install

# 4. Create .env file in root with:
GEMINI_API_KEY=your_api_key_here
CORS_ORIGINS=http://localhost:3001

# 5. Create frontend/.env with:
PORT=3001
REACT_APP_API_URL=http://localhost:5000

# 6. Start backend (PowerShell)
cd backend
python app.py

# 7. Start frontend (new terminal)
cd frontend
npm start

# Frontend runs at http://localhost:3001 (not 3000!)
# Backend API at http://localhost:5000
```

### **Environment Configuration**

**Root `.env` file:**
```env
GEMINI_API_KEY=your_actual_api_key_here
CORS_ORIGINS=http://localhost:3001
```

**`frontend/.env` file:**
```env
PORT=3001
REACT_APP_API_URL=http://localhost:5000
```

*(Replace API key with your key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

---

## 📖 How to Use

### **1. Home Page**
- Overview of PastPortals features
- Quick access to all sections
- Featured topics and civilizations

### **2. Search Historical Topics**
- Click "Search" in sidebar
- Type your question or use voice search 🎤
- Click green search button or press Enter
- View AI-generated response with real historical images
- Images appear on the right (Wikipedia-style layout)
- Text wraps naturally around images

### **3. Multimodal Content Analysis (NEW)**
- Click "Multimodal Explorer" in sidebar to access the unified panel
- **Upload Documents**: PDF, DOCX, TXT, MD, CSV, JSON, HTML (max 50MB)
  - Automatic text extraction and analysis
  - File preview with size display
- **Upload Images**: PNG, JPG, JPEG, WEBP, BMP, TIFF (max 25MB)
  - Automatic OCR text extraction
  - Image thumbnail preview
- **Upload Videos**: MP4, MOV, AVI, MKV, WEBM, M4V (max 500MB)
  - Frame sampling and text extraction
  - Video player preview with controls
- **Record Voice**: Use camera/microphone to capture video queries
  - Click record button to start camera capture
  - Automatic frame processing on upload
- **Upload Progress**: Visual progress bar shows upload status (0-100%)
- **Results Display**:
  - Extracted text in collapsible section
  - AI-generated response or enriched fallback
  - File metadata (name, format, processing method)
  - Processing notes and related Wikipedia topics

### **4. Explore Timeline**
- Navigate through historical periods
- Click on era cards to learn more
- Filter by civilization, war, empire, religion, art

### **5. Visit Museums**
- Browse 6 world-famous museums
- Click museum cards to expand details
- View highlights and artifacts
- Click "Learn More" to visit official museum website

### **6. Voice Search**
- Click the microphone button (turns RED when listening)
- Speak your question clearly
- Button turns BLUE when ready
- Works best with Chrome/Edge
- *Note: Brave browser requires internet connection*

### **7. Language Translation**
- Click language selector (top of search page)
- Choose from 18+ languages
- Content translates instantly
- UI language changes automatically

---

---

## 🧪 Testing & Quality Assurance

### **Backend Tests**
```bash
# Run all backend tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_multimodal_utils.py -v
pytest backend/tests/test_multimodal_routes.py -v

# Run with coverage report
pytest backend/tests/ --cov=backend/utils --cov=backend/routes
```

**Test Coverage**:
- 50+ unit tests across multimodal utilities and routes
- Tests for file extraction (PDF, DOCX, TXT, images, video)
- OCR and frame sampling validation
- Prompt generation and response fallback testing
- Error handling and edge cases

### **Frontend Tests**
```bash
# Run frontend component tests
cd frontend
npm test MultimodalPanel.test.jsx

# Run all tests with coverage
npm test -- --coverage

# Run specific test suite
npm test -- --testNamePattern="MultimodalPanel"
```

**Test Coverage**:
- 40+ React component tests using Jest & React Testing Library
- File validation logic tests
- Upload progress tracking tests
- Mode switching and UI rendering tests
- Results display and error handling tests

### **Manual Testing**
See [MULTIMODAL_TESTING.md](MULTIMODAL_TESTING.md) for comprehensive E2E testing procedures.

---

## 🛠️ Server Management

### **Start Servers**
```bash
# Terminal 1: Backend
cd backend
python app.py
# Runs at http://localhost:5000

# Terminal 2: Frontend
cd frontend
npm start
# Runs at http://localhost:3001
```

### **Check Status**
```powershell
# Check if servers running
Get-Process -Name python -ErrorAction SilentlyContinue  # Backend
Get-Process -Name node -ErrorAction SilentlyContinue     # Frontend
```

### **Stop Servers**
```powershell
# Stop Node (frontend)
Get-Process -Name node | Stop-Process -Force

# Stop Python (backend)
Get-Process -Name python | Stop-Process -Force
```

---

## 🎨 Features in Detail

### **Wikipedia-Style Layout**
- Images float on the right side (320px max-width)
- Text wraps around images naturally
- Professional borders and captions
- Source attribution for all images
- Responsive design: stacks on mobile

### **Image Sources**
- **Wikimedia Commons API**: Free historical photographs
- CORS-friendly, no API key required
- Filters: JPEG/PNG only, minimum 400x300px
- Maximum 3-4 images per search
- Captions with title and source

### **AI Response Quality**
- Minimum 500 words per response
- Structured sections:
  1. Historical background
  2. Key events and timeline
  3. Cultural significance
  4. Impact on civilization
  5. Interesting facts
  6. Modern relevance

---

## 🔧 Troubleshooting

### **Frontend won't start?**
```bash
cd frontend
npm install
npm start
# Should run on http://localhost:3001 (not 3000!)
```

### **Backend won't start?**
```bash
cd backend
pip install -r requirements.txt
python app.py
# Should run on http://localhost:5000
```

### **Tesseract OCR not found?**
- Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`
- Update path in `backend/app.py` if needed: `pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### **File upload fails?**
- Check file size limits: Document (50MB), Image (25MB), Video (500MB)
- Verify file format is allowed (check frontend/src/components/MultimodalPanel.jsx ALLOWED_FORMATS)
- Check backend logs for extraction errors
- Ensure Tesseract is installed for image/video processing

### **Multimodal analysis returns empty response?**
- Check `GEMINI_API_KEY` is valid in `.env`
- Check API quota hasn't exceeded
- Backend will use enriched Wikipedia fallback automatically
- Check browser console for API errors

### **Images not loading?**
- Check internet connection
- Wikimedia Commons requires online access
- Images load from external CDN

### **Voice search not working?**
- Use Chrome or Edge browser (best support)
- Enable microphone permissions
- Brave browser requires internet connection
- Check browser console for errors

### **Port 3001 already in use?**
```powershell
# Find process on port 3001
netstat -ano | findstr :3001

# Kill the process (replace PID)
taskkill /F /PID <PID_NUMBER>
```

### **Port 5000 already in use?**
```powershell
# Find process on port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /F /PID <PID_NUMBER>

# Or change port in backend/app.py
python app.py --port 5001
```

### **CORS errors from frontend?**
- Verify CORS_ORIGINS in `.env` includes `http://localhost:3001`
- Clear browser cache
- Check backend logs for CORS errors

### **Tests failing?**
- Run `pip install -r backend/requirements.txt` to ensure all dependencies installed
- Check Tesseract is installed for multimodal tests
- Run `npm install` in frontend directory for React tests
- See [MULTIMODAL_TESTING.md](MULTIMODAL_TESTING.md) for debugging tips

---

## 📚 API Endpoints

### **Frontend → Backend Communication**

```javascript
// Search historical topics
POST /api/qa
Body: { question: "Tell me about Roman Empire" }

// Multimodal content analysis (NEW)
POST /api/multimodal/analyze
Body: FormData with:
  - file: File object
  - question: string
  - mode: "document|image|video|voice"
Returns: {
  success: boolean,
  mode: string,
  method: string,
  extracted_text: string,
  response: string,
  metadata: {...},
  notes: string[],
  related_topics: [{title, extract}],
  fallback: boolean (true if using Wikipedia fallback)
}

// Translate content
POST /api/translate
Body: { text: "content", targetLanguage: "hi" }

// Summarize text
POST /api/summarize
Body: { text: "long content" }

// Get museum data
GET /api/museums

// Update configuration
POST /api/config
Body: { apiKey: "new_key" }
```

### **Multimodal Processing**

The `/api/multimodal/analyze` endpoint handles:
- **Document Processing**: PDF, DOCX, TXT, MD, CSV, JSON, HTML → text extraction
- **Image Processing**: PNG, JPG, WEBP, TIFF, BMP → OCR with Tesseract
- **Video Processing**: MP4, MOV, AVI, MKV, WEBM, M4V → frame sampling + OCR
- **Voice Processing**: Audio input → transcription and analysis
- **Fallback Mechanism**: When API quota exceeded, returns enriched Wikipedia response

---

## 🌟 Key Technologies

### **Frontend**
- **React 18** - Modern UI framework
- **React Router** - Client-side routing
- **React Testing Library & Jest** - Component testing
- **Lucide React** - Icon library
- **Framer Motion** - Smooth animations
- **CSS Variables** - Theming system

### **Backend**
- **Flask** - Python web framework
- **Google Gemini 2.5 Flash** - Advanced AI model
- **PyMuPDF (fitz)** - PDF text extraction
- **python-docx** - DOCX file processing
- **pdfplumber** - Alternative PDF extraction
- **pytesseract** - OCR for images and video frames
- **OpenCV (cv2)** - Video frame sampling
- **pytest** - Backend testing framework
- **Wikipedia API** - Historical data source
- **Wikimedia Commons API** - Historical image repository
- **Web Speech API** - Voice recognition

---

## � Documentation

- **[MULTIMODAL_IMPLEMENTATION.md](MULTIMODAL_IMPLEMENTATION.md)** - Complete v2 multimodal system implementation details, architecture, and feature breakdown
- **[MULTIMODAL_TESTING.md](MULTIMODAL_TESTING.md)** - Comprehensive testing guide with test commands, E2E procedures, and debugging tips
- **[SETUP.md](SETUP.md)** - Detailed installation and configuration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow documentation

---

## 📋 What's New in v2

✨ **Major Features Added**:
- ✅ Unified multimodal input panel (Document, Image, Video, Voice)
- ✅ File validation with size limits and format checking
- ✅ Upload progress tracking with visual progress bar
- ✅ PDF, DOCX, and text file extraction
- ✅ OCR-based image text extraction using Tesseract
- ✅ Video frame sampling and text analysis
- ✅ Voice input recording and processing
- ✅ File preview (thumbnails, video player)
- ✅ Metadata extraction and display
- ✅ Fallback response generation when API quota exceeded
- ✅ Comprehensive backend unit tests (50+ tests)
- ✅ Frontend component tests (40+ tests with React Testing Library)
- ✅ Full test documentation and E2E testing guide
- ✅ Frontend port changed to 3001 for stability
- ✅ Enhanced error handling and user feedback

---

## 🌐 License

This project is for educational and research purposes. All historical content sourced from Wikipedia and Wikimedia Commons under Creative Commons licenses.

---

## 👥 Credits

- **Historical Data**: Wikipedia Foundation
- **Images**: Wikimedia Commons
- **AI Model**: Google Gemini
- **Museums**: Official museum databases
- **OCR**: Tesseract Engine
- **Framework**: React, Flask, OpenCV
- **UI Icons**: Lucide React

---

## 🚀 Future Enhancements

- [ ] Dark theme toggle
- [ ] Bookmark favorite topics
- [ ] Export to PDF functionality
- [ ] Advanced filtering and search
- [ ] User accounts and history
- [ ] More museum integrations
- [ ] Interactive 3D artifacts
- [ ] Offline mode support

---

## 📞 Support

For issues, questions, or contributions:
- GitHub: [PastPortals - AI](https://github.com/ykjaat6104/PastPortals-AI)
- Report bugs via GitHub Issues
- Check `SERVER_GUIDE.md` for detailed server documentation

---

**PastPortals** - *Bringing History to Life Through Technology* 🌍✨
