import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  AlertCircle,
  Camera,
  FileText,
  Image as ImageIcon,
  Loader2,
  Mic,
  Play,
  Sparkles,
  Square,
  Trash2,
  Upload,
  Video,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import VoiceSearchBar from './VoiceSearchBar';
import { apiService } from '../utils/api';

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
    id: 'voice',
    label: 'Voice',
    icon: Mic,
    hint: 'Speak a question and analyze without a file',
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
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileValidationErrors, setFileValidationErrors] = useState([]);
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const recordingChunksRef = useRef([]);

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

    mediaRecorderRef.current = null;
    recordingChunksRef.current = [];
    setSelectedFile(null);
    setPreviewUrl('');
    setIsRecording(false);
    setRecordingStatus('');
    setResult(null);
    setExtractedText('');
    setAnalysisNotes([]);
    setMetadata(null);
    setErrorMessage('');
    setUploadProgress(0);
    setFileValidationErrors([]);
  };

  const handleModeChange = (mode) => {
    clearSelection();
    setActiveMode(mode);
    setErrorMessage('');
    if (mode === 'voice') {
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

  const handleAnalyze = async () => {
    setLoading(true);
    setErrorMessage('');
    setUploadProgress(0);

    try {
      if ((activeMode !== 'voice') && !selectedFile) {
        throw new Error('Upload a file or switch to voice mode before analyzing.');
      }

      const formData = new FormData();
      formData.append('question', question.trim());
      formData.append('mode', activeMode);
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
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      setResult(response);
      setExtractedText(response.extracted_text || '');
      setAnalysisNotes(response.notes || []);
      setMetadata(response.metadata || null);
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

  const renderModePanel = () => {
    if (activeMode === 'voice') {
      return (
        <div className="multimodal-card multimodal-voice-card">
          <div className="multimodal-card-header">
            <Mic size={18} />
            <h3>Voice prompt</h3>
          </div>
          <VoiceSearchBar
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onSubmit={(event) => {
              event.preventDefault();
              handleAnalyze();
            }}
            placeholder="Speak a question or type it here"
          />
          <p className="multimodal-help">This mode sends only your spoken or typed question to the backend. You can still attach a file by switching to another mode.</p>
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

          <div className="multimodal-question-field">
            <label htmlFor="multimodal-question">Research question</label>
            <textarea
              id="multimodal-question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask what this document, image, or video is about, or add context for the analysis"
              rows={4}
            />
          </div>

          <div className="multimodal-actions">
            <button type="button" className="multimodal-action-btn primary" onClick={handleAnalyze} disabled={loading}>
              {loading ? <Loader2 size={16} className="spin" /> : <Play size={16} />}
              <span>{loading ? 'Analyzing...' : 'Analyze input'}</span>
            </button>
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
          {renderModePanel()}
          <div className="multimodal-card-footer">
            <span className="multimodal-footnote">
              OCR, PDF text extraction, DOCX parsing, and frame sampling are handled on the backend.
            </span>
          </div>
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

          {metadata && (
            <div className="multimodal-metadata-grid">
              <div><strong>Mode</strong><span>{metadata.mode || activeMode}</span></div>
              <div><strong>Format</strong><span>{metadata.extension || 'n/a'}</span></div>
              <div><strong>Method</strong><span>{result?.method || 'analysis'}</span></div>
              {metadata.duration_seconds != null && <div><strong>Duration</strong><span>{metadata.duration_seconds}s</span></div>}
              {metadata.sampled_frames != null && <div><strong>Sampled frames</strong><span>{metadata.sampled_frames}</span></div>}
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
        </section>
      )}
    </div>
  );
};

export default MultimodalPanel;
