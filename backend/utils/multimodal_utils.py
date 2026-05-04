"""
Multimodal extraction and response helpers.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import os
import re

import numpy as np
from PIL import Image

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency
    cv2 = None

try:
    import docx
except Exception:  # pragma: no cover - optional dependency
    docx = None

try:
    import fitz
except Exception:  # pragma: no cover - optional dependency
    fitz = None

try:
    import pytesseract
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif'}
DOCUMENT_EXTENSIONS = {'.txt', '.md', '.csv', '.json', '.html', '.htm'}
PDF_EXTENSIONS = {'.pdf'}
WORD_EXTENSIONS = {'.docx'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}


def _read_text_file(file_path: Path) -> str:
    for encoding in ('utf-8', 'utf-8-sig', 'latin-1'):
        try:
            return file_path.read_text(encoding=encoding)
        except Exception:
            continue
    return ''


def _extract_pdf_text(file_path: Path) -> str:
    if fitz is None:
        return ''

    try:
        document = fitz.open(str(file_path))
        page_texts = []
        for page in document:
            page_texts.append(page.get_text())
        return '\n'.join(page_texts).strip()
    except Exception:
        return ''


def _extract_docx_text(file_path: Path) -> str:
    if docx is None:
        return ''

    try:
        document = docx.Document(str(file_path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        return '\n'.join(paragraphs).strip()
    except Exception:
        return ''


def _ocr_image(file_path: Path) -> tuple[str, list[str]]:
    notes = []
    if pytesseract is None:
        return '', ['OCR package not available']

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        if not text.strip():
            notes.append('OCR returned no readable text')
        return text.strip(), notes
    except Exception as exc:
        notes.append(f'OCR failed: {exc}')
        return '', notes


def _sample_video_frames(file_path: Path, max_frames: int = 8) -> list[Path]:
    """Return sampled frame images written to temporary PNG files."""
    if cv2 is None:
        return []

    temp_dir = file_path.parent / f"{file_path.stem}_frames"
    temp_dir.mkdir(exist_ok=True)

    cap = cv2.VideoCapture(str(file_path))
    if not cap.isOpened():
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total_frames <= 0:
        total_frames = max_frames

    sample_indexes = np.linspace(0, max(total_frames - 1, 0), num=min(max_frames, total_frames), dtype=int)
    frame_paths: list[Path] = []

    for index in sample_indexes:
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            success, frame = cap.read()
            if not success:
                continue

            frame_path = temp_dir / f'frame_{int(index):05d}.png'
            cv2.imwrite(str(frame_path), frame)
            frame_paths.append(frame_path)
        except Exception:
            continue

    cap.release()
    return frame_paths


def _extract_video_text(file_path: Path, max_frames: int = 8) -> tuple[str, list[str], dict]:
    notes = []
    metadata = {
        'frame_count': 0,
        'sampled_frames': 0,
        'duration_seconds': None,
    }

    if cv2 is None:
        return '', ['OpenCV not available for video analysis'], metadata

    try:
        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            return '', ['Unable to open video file'], metadata

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        metadata['frame_count'] = frame_count
        if frame_count > 0 and fps > 0:
            metadata['duration_seconds'] = round(frame_count / fps, 2)

        if frame_count <= 0:
            frame_indexes = list(range(max_frames))
        else:
            frame_indexes = np.linspace(0, frame_count - 1, num=min(max_frames, frame_count), dtype=int).tolist()

        ocr_chunks = []
        for index in frame_indexes:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            success, frame = cap.read()
            if not success:
                continue

            metadata['sampled_frames'] += 1
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            if pytesseract is None:
                notes.append('OCR package not available for video frames')
                break

            text = pytesseract.image_to_string(image).strip()
            if text:
                ocr_chunks.append(text)

        cap.release()
        return '\n\n'.join(ocr_chunks).strip(), notes, metadata
    except Exception as exc:
        return '', [f'Video OCR failed: {exc}'], metadata


def extract_multimodal_content(file_path: str | Path, filename: str | None = None, input_mode: str = 'auto') -> dict:
    """Extract readable content from a document, image, or video file."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    resolved_mode = (input_mode or 'auto').lower()

    metadata = {
        'filename': filename or path.name,
        'extension': suffix,
        'mode': resolved_mode,
        'size_bytes': path.stat().st_size if path.exists() else None,
    }

    if suffix in DOCUMENT_EXTENSIONS:
        text = _read_text_file(path)
        return {
            'text': text,
            'method': 'text-file',
            'notes': ['Plain-text document extracted successfully' if text else 'Text file contained no readable content'],
            'metadata': metadata,
        }

    if suffix in PDF_EXTENSIONS:
        text = _extract_pdf_text(path)
        notes = ['PDF text extracted using PyMuPDF'] if text else ['No embedded PDF text found; OCR may be needed']
        return {
            'text': text,
            'method': 'pdf',
            'notes': notes,
            'metadata': metadata,
        }

    if suffix in WORD_EXTENSIONS:
        text = _extract_docx_text(path)
        return {
            'text': text,
            'method': 'docx',
            'notes': ['DOCX paragraphs extracted successfully' if text else 'DOCX contained no readable paragraphs'],
            'metadata': metadata,
        }

    if suffix in IMAGE_EXTENSIONS or resolved_mode == 'image':
        text, notes = _ocr_image(path)
        return {
            'text': text,
            'method': 'ocr-image',
            'notes': notes,
            'metadata': metadata,
        }

    if suffix in VIDEO_EXTENSIONS or resolved_mode == 'video':
        text, notes, video_meta = _extract_video_text(path)
        metadata.update(video_meta)
        return {
            'text': text,
            'method': 'ocr-video',
            'notes': notes,
            'metadata': metadata,
        }

    # Last resort: try to read as text.
    text = _read_text_file(path)
    return {
        'text': text,
        'method': 'generic-text',
        'notes': ['Fallback text extraction used' if text else 'No readable content extracted'],
        'metadata': metadata,
    }


def generate_multimodal_prompt(question: str, input_mode: str, extracted_text: str = '', file_metadata: dict | None = None, notes: list[str] | None = None) -> str:
    file_metadata = file_metadata or {}
    notes = notes or []
    truncated_text = extracted_text.strip()[:12000]

    return f"""
You are a world-class historical research assistant.

You are analyzing a user-provided {input_mode} input. Use the extracted content to produce a detailed, structured response.

Requirements:
- Write approximately 900-1100 words.
- Use markdown headings.
- Include: Overview, Historical Context, Key Facts, Cultural or Visual Analysis, Modern Legacy, Related Topics.
- If the extracted text is noisy, explain that and interpret cautiously.
- Do not mention external source labels like Wikipedia.
- If the upload is a document, summarize the document's historical meaning and themes.
- If the upload is an image, describe visible text, symbols, people, places, or stylistic clues.
- If the upload is a video, infer the subject from sampled frames and any OCR text.

Question from user:
{question}

File metadata:
{file_metadata}

Extraction notes:
{notes}

Extracted content:
{truncated_text or 'No readable text was extracted.'}

Return a comprehensive answer with enough detail to fill a full page.
""".strip()


def generate_multimodal_fallback_response(question: str, input_mode: str, extracted_text: str = '', file_metadata: dict | None = None, notes: list[str] | None = None, related_topics: list[dict] | None = None) -> str:
    file_metadata = file_metadata or {}
    notes = notes or []
    related_topics = related_topics or []

    response_parts = [f"## Multimodal Analysis: {question or file_metadata.get('filename', 'Uploaded Input')}"]
    response_parts.append(f"\n### Overview\nThis {input_mode} input appears to relate to a historical, cultural, or informational topic. The content below is assembled from the uploaded material and available reference context.")

    if extracted_text.strip():
        response_parts.append(f"\n### Extracted Content\n{extracted_text.strip()[:6000]}")
    else:
        response_parts.append("\n### Extracted Content\nNo readable text could be extracted from the uploaded file, so the response relies on the user question and available metadata.")

    if notes:
        response_parts.append("\n### Processing Notes\n" + '\n'.join(f"- {note}" for note in notes))

    if file_metadata:
        response_parts.append(f"\n### File Details\n- Filename: {file_metadata.get('filename', 'Unknown')}\n- Mode: {file_metadata.get('mode', 'auto')}\n- Format: {file_metadata.get('extension', 'n/a')}")
        if file_metadata.get('frame_count') is not None:
            response_parts.append(f"- Video frames detected: {file_metadata.get('frame_count')}")
        if file_metadata.get('sampled_frames') is not None:
            response_parts.append(f"- Sampled frames: {file_metadata.get('sampled_frames')}")
        if file_metadata.get('duration_seconds') is not None:
            response_parts.append(f"- Approximate duration: {file_metadata.get('duration_seconds')} seconds")

    response_parts.append("\n### Historical Context\nThe uploaded material should be interpreted in relation to its period, region, style, or purpose. For documents, that means the document type, authorship, and historical setting. For images, it means iconography, visual style, inscriptions, and composition. For video, it means the sequence of frames, spoken or written cues, and any recurring symbols or locations.")
    response_parts.append("\n### Key Facts\n- This fallback response is generated because live Gemini output is currently unavailable or incomplete.\n- The pipeline still preserves extracted text so the answer can be expanded later.\n- You can refine the upload or ask a targeted follow-up question to improve precision.")
    response_parts.append("\n### Cultural or Visual Analysis\nThe material may contain references to people, places, artworks, rituals, events, architecture, or textual traditions. Those clues help place it within broader historical and cultural narratives.")
    response_parts.append("\n### Modern Legacy\nEven when the upload is old or archival, it may still influence education, public memory, museum interpretation, or media today.")

    if related_topics:
        response_parts.append("\n### Related Topics\n")
        for topic in related_topics[:5]:
            title = topic.get('title', 'Related Topic')
            extract = topic.get('extract', '').strip()
            if extract:
                response_parts.append(f"#### {title}\n{extract}")

    return '\n'.join(response_parts)


def summarize_keywords(text: str, limit: int = 12) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-']+", text.lower())
    filtered = [word for word in words if len(word) > 3]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(limit)]