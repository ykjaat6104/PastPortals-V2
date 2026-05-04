# Multimodal System - Test Guide and Instructions

## Overview

This guide covers how to run and validate the multimodal input pipeline system, including document OCR, image analysis, video processing, and unified frontend UI.

---

## Backend Testing

### Prerequisites

```powershell
# Activate Python virtual environment
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .venv\Scripts\Activate.ps1

# Install test dependencies
pip install pytest pytest-cov
```

### Run Backend Unit Tests

```bash
# From project root
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_multimodal_utils.py -v
pytest tests/test_multimodal_routes.py -v

# Run with coverage report
pytest tests/ --cov=utils --cov=routes --cov-report=html
```

### Test Coverage

**test_multimodal_utils.py** (12 test classes, ~35 tests)
- Text file extraction (UTF-8, empty files, error handling)
- Multimodal content extraction (TXT, MD, JSON, PDF, DOCX, images, video)
- Prompt generation (document, image, video modes)
- Fallback response generation
- Keyword summarization
- Metadata handling (file size, extension, mode)
- Error handling and edge cases

**test_multimodal_routes.py** (3 test classes, ~15 tests)
- `/api/multimodal/analyze` endpoint with various file types
- Request validation (missing file, missing question)
- Metadata extraction and reporting
- Fallback flag handling
- Related topics generation
- File cleanup after processing
- Error scenarios (invalid mode, malformed requests, large inputs)

---

## Frontend Testing

### Prerequisites

```bash
# Install from frontend directory
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest

# Or add to package.json and run:
npm install
```

### Run Frontend Tests

```bash
# From frontend directory
npm test

# Run specific test file
npm test MultimodalPanel.test.jsx

# Run with coverage
npm test -- --coverage
```

### Test Coverage

**MultimodalPanel.test.jsx** (9 test suites, ~40 tests)
- Component rendering (all mode options, default state)
- Mode switching (Document, Image, Video, Voice)
- File validation (size limits, format restrictions, error display)
- File display (name, size formatting)
- Question input handling
- Analysis workflow (API calls, loading states, results display)
- Error handling and toast notifications
- Clear functionality
- File size formatting (Bytes, KB, MB)
- Metadata display and analysis notes

---

## End-to-End Testing

### Manual Testing Steps

#### 1. Start Backend Server

```powershell
# From project root
python -m backend.app

# Output should show:
# ============================================================
# PASTPORTALS - Backend Server
# ============================================================
# Environment: production
# Gemini AI: Configured
# Wikipedia API: Ready
# ============================================================
# Server Ready - http://0.0.0.0:5000
```

#### 2. Start Frontend Development Server (New Terminal)

```bash
cd frontend
npm start
# Frontend runs on http://localhost:3001
```

#### 3. Test Document Upload

1. Navigate to http://localhost:3001/multimodal
2. Stay in "Document" mode
3. Create a test file:
   ```
   # Ancient Rome
   
   Rome was founded in 753 BC and became one of history's greatest civilizations.
   The Roman Empire lasted for over 1000 years.
   ```
   Save as `rome.md`
4. Upload the file
5. Enter question: "What was Roman civilization known for?"
6. Click "Analyze input"
7. Verify:
   - Progress bar appears and completes
   - Extracted text shows in results
   - Generated response appears (may be fallback if Gemini quota exceeded)
   - Metadata displays filename, format, and size

#### 4. Test Image OCR

1. Switch to "Image" mode
2. Upload a screenshot or photo with visible text
3. Enter question: "What text is visible in this image?"
4. Click "Analyze input"
5. Verify:
   - OCR extracts visible text
   - Response contextualizes the content
   - Notes show OCR status

#### 5. Test Video Analysis

1. Switch to "Video" mode
2. Option A: Upload a short video file (MP4, WebM, etc.)
3. Option B: Click "Record from camera" to capture video (5-10 seconds)
4. Enter question: "Describe what happens in this video"
5. Click "Analyze input"
6. Verify:
   - Frame extraction happens (1-2 seconds delay)
   - Response describes scenes/text from sampled frames
   - Metadata shows sampled frame count and duration

#### 6. Test Voice Mode

1. Switch to "Voice" mode
2. Type or speak: "Tell me about the Renaissance"
3. Click "Analyze input"
4. Verify:
   - No file required
   - Response appears (may use Wikipedia if Gemini unavailable)
   - Answer addresses the question

---

## Validation Checklist

### File Validation
- [ ] Oversized documents (>50 MB) rejected with error message
- [ ] Oversized images (>25 MB) rejected with error message
- [ ] Oversized videos (>500 MB) rejected with error message
- [ ] Unsupported formats show helpful error (lists allowed formats)
- [ ] Valid formats accepted without errors
- [ ] File size displayed in human-readable format (B, KB, MB, GB)

### Upload Progress
- [ ] Progress bar appears during analysis
- [ ] Progress text shows percentage
- [ ] Progress bar completes when analysis finishes
- [ ] Analyze button disabled during processing

### Error Handling
- [ ] Network errors show clear message
- [ ] Invalid API responses show user-friendly error
- [ ] Missing API configuration shows helpful message
- [ ] File cleanup happens after processing (no temp files left)

### Results Display
- [ ] Extracted text visible in collapsible section
- [ ] Generated/fallback response displays in markdown
- [ ] Processing notes list appears if present
- [ ] Metadata grid shows filename, format, method, duration (if video)
- [ ] Related topics display if available

---

## Test Commands Summary

```powershell
# Backend tests (PowerShell, from project root)
cd backend
pytest tests/ -v --tb=short
pytest tests/test_multimodal_utils.py -v
pytest tests/test_multimodal_routes.py -v
pytest tests/ --cov=utils.multimodal_utils --cov=routes.multimodal_routes

# Frontend tests (from frontend directory)
npm test
npm test -- --coverage
npm test -- --watch

# Full end-to-end (start both servers in separate terminals)
# Terminal 1:
python -m backend.app

# Terminal 2:
cd frontend
npm start

# Test in browser at http://localhost:3001/multimodal
```

---

## Debugging Tips

### Backend Issues

**ImportError: No module named 'pytesseract'**
```powershell
pip install pytesseract pdfplumber python-docx opencv-python-headless pymupdf
```

**PDF extraction not working**
- Requires `pdfplumber` for text extraction
- Falls back to OCR if no embedded text
- Verify PDF is not encrypted

**OCR returning empty text**
- Tesseract must be installed on system (Windows: download installer)
- Image may have no readable text
- Try increasing image contrast preprocessing

**Video frame sampling fails**
- Requires `opencv-python-headless` installed
- Video file format may not be supported
- Check video codec (H.264 recommended)

### Frontend Issues

**Progress bar doesn't appear**
- Check browser console for JavaScript errors
- Verify API endpoint is reachable
- Check CORS configuration

**File validation doesn't trigger**
- Ensure MultimodalPanel.jsx was replaced (not original)
- Check browser console for JavaScript errors
- Verify FILE_SIZE_LIMITS and ALLOWED_FORMATS are defined

**Images don't preview**
- Check browser permissions for file reading
- Verify image format is supported
- Ensure file size is under 25 MB

**Video recording fails**
- Browser must support MediaRecorder API
- User must grant camera/microphone permissions
- HTTPS required in production (HTTP OK for localhost)

---

## File Structure

```
backend/
  tests/
    test_multimodal_utils.py        # Utility function tests
    test_multimodal_routes.py       # Route endpoint tests
  utils/
    multimodal_utils.py             # Extraction & response generation
  routes/
    multimodal_routes.py            # API endpoints

frontend/
  src/
    components/
      MultimodalPanel.jsx           # Main UI component (enhanced)
      MultimodalPanel.test.jsx      # Component tests
    styles/
      components.css                # Includes progress bar styles
    utils/
      api.js                        # API service with analyzeMultimodal()
```

---

## Next Steps

1. **Run Backend Tests**: `pytest tests/ -v` to verify utilities and routes
2. **Run Frontend Tests**: `npm test` to verify component behavior
3. **Manual E2E**: Upload documents/images/videos through UI
4. **Performance Testing**: Test with large files near size limits
5. **Load Testing**: Simulate concurrent multimodal requests
6. **CI/CD Integration**: Add tests to GitHub Actions workflow

---

## Documentation Links

- Backend: See docstrings in `backend/utils/multimodal_utils.py` and `backend/routes/multimodal_routes.py`
- Frontend: See JSDoc comments in `frontend/src/components/MultimodalPanel.jsx`
- API: `/api/multimodal/analyze` (POST) - see route docstring for full schema

---

**Last Updated**: May 5, 2026
**Status**: All features implemented and tested
**Test Coverage**: ~50 tests (35 backend, ~40 frontend)
