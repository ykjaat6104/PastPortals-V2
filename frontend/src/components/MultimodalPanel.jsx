import React, { useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  AlertCircle,
  Camera,
  FileText,
  Image as ImageIcon,
  Loader2,
  Mic,
  Search,
  Sparkles,
  Square,
  Trash2,
  Upload,
  Video,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiService } from '../utils/api';
import { getTopicImages } from '../utils/imageSearch';

const MODE_OPTIONS = [
  {
    id: 'document',
    label: 'Document',
    icon: FileText,
    hint: 'PDF, DOCX, TXT, or Markdown files',
  },
  {
    id: 'image',
    label: 'Image',
    icon: ImageIcon,
    hint: 'Photos, screenshots, posters, or scanned pages',
  },
  {
    id: 'video',
    label: 'Video',
    icon: Video,
    hint: 'Uploaded clips or a short camera recording',
  },
  {
    id: 'prompt',
    label: 'Text + Voice',
    icon: Mic,
    hint: 'Use one prompt box for typed or voice-style queries',
  },
];

const FILE_SIZE_LIMITS = {
  document: 50 * 1024 * 1024, // 50 MB
  image: 25 * 1024 * 1024, // 25 MB
  video: 500 * 1024 * 1024, // 500 MB
};

const ALLOWED_FORMATS = {
  document: ['.pdf', '.docx', '.txt', '.md', '.csv', '.json', '.html', '.htm'],
  image: ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif'],
  video: ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'],
};

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function validateFile(file, mode) {
  const errors = [];
  
  // Check file size
  const sizeLimit = FILE_SIZE_LIMITS[mode];
  if (file.size > sizeLimit) {
    errors.push(`File size (${formatFileSize(file.size)}) exceeds limit of ${formatFileSize(sizeLimit)}`);
  }
  
  // Check file format
  const fileName = file.name.toLowerCase();
  const fileExt = '.' + fileName.split('.').pop();
  const allowedFormats = ALLOWED_FORMATS[mode];
  if (!allowedFormats.includes(fileExt)) {
    errors.push(`File format not supported. Allowed: ${allowedFormats.join(', ')}`);
  }
  
  return errors;
}

const MultimodalPanel = () => {
  const location = useLocation();
  const [activeMode, setActiveMode] = useState('document');
  const [question, setQuestion] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('');
  const [result, setResult] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [analysisNotes, setAnalysisNotes] = useState([]);
  const [metadata, setMetadata] = useState(null);
  const [resultImages, setResultImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileValidationErrors, setFileValidationErrors] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const recordingChunksRef = useRef([]);
  const speechRecognitionRef = useRef(null);
  const lastResultIndexRef = useRef(-1);
  const lastAutoSearchQueryRef = useRef('');
  const handleAnalyzeRef = useRef(null);

  const normalizeQuery = (value) => {
    if (typeof value === 'string') {
      return value.replace(/\s+/g, ' ').trim();
    }

    if (typeof value === 'number') {
      return String(value);
    }

    return '';
  };

  const buildVisualQuery = (response, fallbackMode) => {
    const candidates = [
      normalizeQuery(question),
      normalizeQuery(response?.response),
      normalizeQuery(response?.extracted_text),
      normalizeQuery(metadata?.filename),
      normalizeQuery(selectedFile?.name),
      normalizeQuery(response?.related_topics?.[0]?.title),
      fallbackMode,
    ];

    const query = candidates.find((candidate) => candidate && candidate.length >= 3) || '';
    return query.length > 120 ? query.slice(0, 120) : query;
  };

  // Initialize Speech Recognition on mount
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition && !speechRecognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        lastResultIndexRef.current = -1;
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = Math.max(0, lastResultIndexRef.current + 1); i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript;
            lastResultIndexRef.current = i;
          }
        }
        if (transcript.trim()) {
          setQuestion((prev) => prev + (prev.trim() ? ' ' : '') + transcript.trim());
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setErrorMessage(`Voice input error: ${event.error}`);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      speechRecognitionRef.current = recognition;
    }
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [previewUrl]);

  const clearSelection = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (isListening && speechRecognitionRef.current) {
      speechRecognitionRef.current.stop();
    }

    mediaRecorderRef.current = null;
    recordingChunksRef.current = [];
    setSelectedFile(null);
    setPreviewUrl('');
    setIsRecording(false);
    setIsListening(false);
    setRecordingStatus('');
    setResult(null);
    setExtractedText('');
    setAnalysisNotes([]);
    setMetadata(null);
    setResultImages([]);
    setErrorMessage('');
    setUploadProgress(0);
    setFileValidationErrors([]);
  };

  const handleVoiceInput = () => {
    if (!speechRecognitionRef.current) {
      setErrorMessage('Speech recognition is not supported in your browser.');
      return;
    }

    if (isListening) {
      speechRecognitionRef.current.stop();
      setIsListening(false);
    } else {
      setErrorMessage('');
      speechRecognitionRef.current.start();
    }
  };

  const handleModeChange = (mode) => {
    clearSelection();
    setActiveMode(mode);
    setErrorMessage('');
    if (mode === 'prompt') {
      setRecordingStatus('');
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    // Validate file
    const errors = validateFile(file, activeMode);
    if (errors.length > 0) {
      setFileValidationErrors(errors);
      setSelectedFile(null);
      setPreviewUrl('');
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const objectUrl = URL.createObjectURL(file);
    setSelectedFile(file);
    setPreviewUrl(objectUrl);
    setErrorMessage('');
    setFileValidationErrors([]);
    setResult(null);
    setExtractedText('');
    setAnalysisNotes([]);
    setMetadata(null);
    setResultImages([]);

    if (activeMode === 'video' && file.type.startsWith('video/')) {
      setRecordingStatus('Video file ready for analysis.');
    }
  };

  const stopRecordingStream = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
  };

  const handleRecordVideo = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      stopRecordingStream();
      setIsRecording(false);
      setRecordingStatus('Recording stopped. Preparing the clip.');
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setErrorMessage('Camera recording is not supported in this browser. Upload a video file instead.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      mediaStreamRef.current = stream;
      recordingChunksRef.current = [];

      const preferredTypes = [
        'video/webm;codecs=vp9,opus',
        'video/webm;codecs=vp8,opus',
        'video/webm',
      ];
      const mimeType = preferredTypes.find((type) => window.MediaRecorder?.isTypeSupported(type));
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordingChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(recordingChunksRef.current, { type: recorder.mimeType || 'video/webm' });
        const recordedFile = new File([blob], 'camera-recording.webm', { type: blob.type || 'video/webm' });
        const recordedUrl = URL.createObjectURL(blob);

        if (previewUrl) {
          URL.revokeObjectURL(previewUrl);
        }

        setSelectedFile(recordedFile);
        setPreviewUrl(recordedUrl);
        setRecordingStatus('Camera clip captured. Ready for analysis.');
        setIsRecording(false);
        stopRecordingStream();
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setActiveMode('video');
      setRecordingStatus('Recording camera video. Click stop when you have enough footage.');
      setErrorMessage('');
    } catch (err) {
      setErrorMessage('Unable to access the camera. Upload a video file or allow camera permissions.');
      toast.error('Camera access is required for live recording');
    }
  };

  const handleAnalyze = async (questionOverride = null, modeOverride = null) => {
    const effectiveMode = modeOverride || activeMode;
    const effectiveQuestion = normalizeQuery(questionOverride ?? question);

    setLoading(true);
    setErrorMessage('');
    setUploadProgress(0);
    setResultImages([]);

    try {
      if (effectiveMode === 'prompt' && !effectiveQuestion) {
        throw new Error('Enter a query in Text + Voice mode before searching.');
      }

      if ((effectiveMode !== 'prompt') && !selectedFile) {
        throw new Error('Upload a file or switch to Text + Voice mode before analyzing.');
      }

      const formData = new FormData();
      formData.append('question', effectiveQuestion);
      // Backend expects known mode values; use voice for prompt-only searches.
      formData.append('mode', effectiveMode === 'prompt' ? 'voice' : effectiveMode);
      if (selectedFile) {
        formData.append('file', selectedFile);
      }

      // Simulate upload progress (real progress would require XMLHttpRequest or fetch progress events)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          const next = prev + Math.random() * 30;
          return next > 95 ? 95 : next;
        });
      }, 200);

      const response = await apiService.analyzeMultimodal(formData);

      const visualQuery = buildVisualQuery(response, effectiveMode);
      const images = visualQuery ? await getTopicImages(visualQuery, 4).catch(() => []) : [];
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      setResult(response);
      setExtractedText(response.extracted_text || '');
      setAnalysisNotes(response.notes || []);
      setMetadata(response.metadata || null);
      setResultImages(Array.isArray(response.related_images) && response.related_images.length > 0 ? response.related_images : (Array.isArray(images) ? images : []));
      toast.success(response.fallback ? 'Analysis completed with fallback context.' : 'Multimodal analysis ready.');
    } catch (err) {
      const message = err.message || 'Analysis failed';
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  handleAnalyzeRef.current = handleAnalyze;

  useEffect(() => {
    const incomingQuery = normalizeQuery(location.state?.query);
    if (!incomingQuery) {
      return;
    }

    setActiveMode('prompt');
    setQuestion(incomingQuery);

    if (location.state?.autoSearch && lastAutoSearchQueryRef.current !== incomingQuery) {
      lastAutoSearchQueryRef.current = incomingQuery;
      handleAnalyzeRef.current?.(incomingQuery, 'prompt');
    }
  }, [location.state]);

  const renderSourcePreview = () => {
    if (!previewUrl || !selectedFile) {
      return null;
    }

    return (
      <div className="multimodal-source-preview">
        <div className="multimodal-source-preview-header">
          <strong>Source preview</strong>
          <span>{selectedFile.name}</span>
        </div>
        {activeMode === 'video' ? (
          <video src={previewUrl} controls className="multimodal-video-preview" />
        ) : (
          <img src={previewUrl} alt="Uploaded preview" className="multimodal-image-preview" />
        )}
      </div>
    );
  };

  const renderModePanel = () => {
    if (activeMode === 'prompt') {
      return (
        <div className="multimodal-card multimodal-voice-card">
          <div className="multimodal-card-header">
            <Mic size={18} />
            <h3>Text and voice prompt</h3>
          </div>
          <div className="multimodal-prompt-row">
            <input
              className="multimodal-prompt-input"
              aria-label="Text and voice query"
              placeholder="Type your question here"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  handleAnalyze();
                }
              }}
            />
            <button
              type="button"
              onClick={handleVoiceInput}
              title={isListening ? 'Stop listening' : 'Start voice input'}
              className={`multimodal-voice-btn ${isListening ? 'listening' : ''}`}
              aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
            >
              <Mic size={18} />
            </button>
            <button
              type="button"
              onClick={handleAnalyze}
              title="Search"
              className="multimodal-search-btn"
              disabled={loading}
            >
              {loading ? <Loader2 size={15} className="spin" /> : <Search size={16} />}
            </button>
          </div>
          <p className="multimodal-help">Click the microphone icon to speak your query, or type directly into the input field, then click search.</p>
        </div>
      );
    }

    if (activeMode === 'document') {
      return (
        <div className="multimodal-card">
          <div className="multimodal-card-header">
            <FileText size={18} />
            <h3>Document upload</h3>
          </div>
          <label className="multimodal-upload-zone" htmlFor="multimodal-document-upload">
            <Upload size={28} />
            <strong>Drop or choose a document</strong>
            <span>PDF, DOCX, TXT, MD, CSV, JSON, or HTML • Max 50 MB</span>
          </label>
          <input id="multimodal-document-upload" type="file" accept=".pdf,.docx,.txt,.md,.csv,.json,.html,.htm" onChange={handleFileChange} className="multimodal-file-input" />
          {selectedFile && <div className="multimodal-file-chip">{selectedFile.name} ({formatFileSize(selectedFile.size)})</div>}
        </div>
      );
    }

    if (activeMode === 'image') {
      return (
        <div className="multimodal-card">
          <div className="multimodal-card-header">
            <ImageIcon size={18} />
            <h3>Image OCR</h3>
          </div>
          <label className="multimodal-upload-zone" htmlFor="multimodal-image-upload">
            <Camera size={28} />
            <strong>Upload or capture an image</strong>
            <span>Use a photo, screenshot, scan, poster, or handwritten page • Max 25 MB</span>
          </label>
          <input id="multimodal-image-upload" type="file" accept="image/*" capture="environment" onChange={handleFileChange} className="multimodal-file-input" />
          {selectedFile && <div className="multimodal-file-chip">{selectedFile.name} ({formatFileSize(selectedFile.size)})</div>}
          {previewUrl && <img src={previewUrl} alt="Selected upload preview" className="multimodal-image-preview" />}
        </div>
      );
    }

    return (
      <div className="multimodal-card">
        <div className="multimodal-card-header">
          <Video size={18} />
          <h3>Video analysis</h3>
        </div>
        <label className="multimodal-upload-zone" htmlFor="multimodal-video-upload">
          <Upload size={28} />
          <strong>Upload a video file</strong>
          <span>MP4, MOV, AVI, MKV, WEBM, or M4V • Max 500 MB</span>
        </label>
        <input id="multimodal-video-upload" type="file" accept="video/*" onChange={handleFileChange} className="multimodal-file-input" />
        <div className="multimodal-record-row">
          <button type="button" className={`multimodal-record-btn ${isRecording ? 'recording' : ''}`} onClick={handleRecordVideo}>
            {isRecording ? <Square size={16} /> : <Camera size={16} />}
            <span>{isRecording ? 'Stop camera capture' : 'Record from camera'}</span>
          </button>
        </div>
        {recordingStatus && <p className="multimodal-help">{recordingStatus}</p>}
        {selectedFile && <div className="multimodal-file-chip">{selectedFile.name} ({formatFileSize(selectedFile.size)})</div>}
        {previewUrl && (
          <video src={previewUrl} controls className="multimodal-video-preview" />
        )}
      </div>
    );
  };

  const renderFileValidationErrors = () => {
    if (fileValidationErrors.length === 0) return null;
    return (
      <div className="multimodal-error">
        <AlertCircle size={16} />
        <div>
          <strong>File validation failed:</strong>
          <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.25rem', fontSize: 'var(--font-size-sm)' }}>
            {fileValidationErrors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  const renderUploadProgress = () => {
    if (!loading || uploadProgress === 0) return null;
    return (
      <div className="multimodal-progress">
        <div className="multimodal-progress-bar">
          <div className="multimodal-progress-fill" style={{ width: `${uploadProgress}%` }} />
        </div>
        <span className="multimodal-progress-text">{Math.round(uploadProgress)}% processing</span>
      </div>
    );
  };

  return (
    <div className="page-shell multimodal-page">
      <div className="page-hero multimodal-hero">
        <div className="page-hero-copy">
          <div className="page-badge">
            <Sparkles size={14} />
            Unified input pipeline
          </div>
          <h1>Multimodal analysis studio</h1>
          <p>
            Upload a document, inspect an image, record a short clip, or speak a question. The backend extracts readable
            text first, then expands it into a full historical response.
          </p>
        </div>
      </div>

      <div className="multimodal-layout">
        <section className="multimodal-card multimodal-controls-card">
          <div className="multimodal-card-header">
            <Sparkles size={18} />
            <h3>Mode</h3>
          </div>
          <div className="multimodal-mode-grid">
            {MODE_OPTIONS.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.id}
                  type="button"
                  className={`multimodal-mode-chip ${activeMode === option.id ? 'active' : ''}`}
                  onClick={() => handleModeChange(option.id)}
                >
                  <Icon size={18} />
                  <span>{option.label}</span>
                </button>
              );
            })}
          </div>
          <p className="multimodal-help">{MODE_OPTIONS.find((option) => option.id === activeMode)?.hint}</p>

          {/* Research question textarea removed per UI request. Use the prompt on the right to enter queries. */}

          <div className="multimodal-actions">
            <button type="button" className="multimodal-action-btn secondary" onClick={clearSelection}>
              <Trash2 size={16} />
              <span>Clear</span>
            </button>
          </div>

          {renderUploadProgress()}
          {renderFileValidationErrors()}
          {errorMessage && (
            <div className="multimodal-error">
              <AlertCircle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}
        </section>

        <section className="multimodal-card multimodal-input-card">
          {activeMode !== 'prompt' && (
            <div className="multimodal-prompt-row">
              <input
                className="multimodal-prompt-input"
                aria-label="Search prompt"
                placeholder="Optional context: Enter a query or question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    handleAnalyze();
                  }
                }}
              />
              <button
                type="button"
                onClick={handleAnalyze}
                title="Search"
                className="multimodal-search-btn"
                disabled={loading}
              >
                {loading ? <Loader2 size={15} className="spin" /> : <Search size={16} />}
              </button>
            </div>
          )}
          {renderModePanel()}
        </section>
      </div>

      {(result || extractedText || metadata || analysisNotes.length > 0) && (
        <section className="multimodal-results-card">
          <div className="multimodal-results-header">
            <div>
              <p className="section-kicker">Analysis output</p>
              <h2>{result?.fallback ? 'Fallback-rich response' : 'Generated response'}</h2>
            </div>
            {metadata?.filename && <span className="multimodal-file-chip">{metadata.filename}</span>}
          </div>

          {renderSourcePreview()}

          {metadata && (
            <div className="multimodal-metadata-grid">
              <div><strong>Mode</strong><span>{metadata.mode || activeMode}</span></div>
              <div><strong>Format</strong><span>{metadata.extension || 'n/a'}</span></div>
              <div><strong>Method</strong><span>{result?.method || 'analysis'}</span></div>
              {metadata.duration_seconds != null && <div><strong>Duration</strong><span>{metadata.duration_seconds}s</span></div>}
              {metadata.sampled_frames != null && <div><strong>Sampled frames</strong><span>{metadata.sampled_frames}</span></div>}
            </div>
          )}

          {resultImages.length > 0 && (
            <div className="multimodal-visual-gallery">
              <div className="multimodal-section-title-row">
                <h3>Visual references</h3>
                <span>Related images for context</span>
              </div>
              <div className="multimodal-visual-grid">
                {resultImages.map((image, index) => (
                  <figure key={`${image.title}-${index}`} className="multimodal-visual-card">
                    <img src={image.url} alt={image.title} loading="lazy" />
                    <figcaption>
                      <strong>{image.title}</strong>
                      <span>{image.source}</span>
                    </figcaption>
                  </figure>
                ))}
              </div>
            </div>
          )}

          {analysisNotes.length > 0 && (
            <div className="multimodal-notes">
              <h3>Processing notes</h3>
              <ul>
                {analysisNotes.map((note, index) => (
                  <li key={`${note}-${index}`}>{note}</li>
                ))}
              </ul>
            </div>
          )}

          {extractedText && (
            <div className="multimodal-extracted">
              <h3>Extracted text</h3>
              <pre>{extractedText}</pre>
            </div>
          )}

          {result?.response && (
            <article className="multimodal-response">
              <ReactMarkdown>{result.response}</ReactMarkdown>
            </article>
          )}

          {Array.isArray(result?.related_topics) && result.related_topics.length > 0 && (
            <div className="multimodal-related-topics">
              <div className="multimodal-section-title-row">
                <h3>Related topics</h3>
                <span>Use these for deeper follow-up searches</span>
              </div>
              <div className="multimodal-related-grid">
                {result.related_topics.slice(0, 4).map((topic, index) => (
                  <article key={`${topic.title}-${index}`} className="multimodal-related-card">
                    <h4>{topic.title || 'Related topic'}</h4>
                    <p>{topic.extract || 'No additional description was returned.'}</p>
                  </article>
                ))}
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default MultimodalPanel;
