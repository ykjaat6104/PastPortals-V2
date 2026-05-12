"""
Routes for analyzing uploaded documents, images, and videos.
"""
from __future__ import annotations

from pathlib import Path
import tempfile

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from utils.ai_utils import generate_content, is_gemini_configured
from utils.wikipedia_utils import search_and_summarize
from utils.multimodal_utils import (
    extract_multimodal_content,
    generate_multimodal_fallback_response,
    generate_multimodal_prompt,
)
from utils.crag_utils import apply_crag
from utils.vector_utils import load_vector_db
from config import get_config


multimodal_bp = Blueprint('multimodal', __name__, url_prefix='/api/multimodal')


def _extract_question_payload() -> tuple[str, str]:
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        return (payload.get('question', '') or '').strip(), (payload.get('mode', 'auto') or 'auto').strip().lower()

    return (request.form.get('question', '') or '').strip(), (request.form.get('mode', 'auto') or 'auto').strip().lower()


def _save_upload(uploaded_file) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix='pastportals_multimodal_'))
    filename = secure_filename(uploaded_file.filename or 'upload')
    file_path = temp_dir / filename
    uploaded_file.save(str(file_path))
    return file_path


def _build_related_topics(search_term: str) -> list[dict]:
    topics = []
    if not search_term:
        return topics

    try:
        result = search_and_summarize(search_term)
        if isinstance(result, dict):
            summary = result.get('summary') or result.get('extract') or ''
            if summary:
                topics.append({
                    'title': result.get('title', search_term),
                    'extract': summary,
                })
    except Exception:
        pass

    return topics


@multimodal_bp.route('/analyze', methods=['POST'])
def analyze_multimodal_input():
    """
    Analyze multimodal input using CRAG (Correction + RAG) pipeline
    for accurate, fact-checked responses
    """
    question, input_mode = _extract_question_payload()
    uploaded_file = request.files.get('file') or request.files.get('upload')

    if not question and not uploaded_file:
        return jsonify({
            'success': False,
            'error': 'Provide a question, a file upload, or both.',
        }), 400

    file_details = {
        'filename': None,
        'mode': input_mode,
        'extension': None,
    }
    extracted_text = ''
    extraction_notes: list[str] = []
    extraction_method = 'text-only'

    # Step 1: Extract content from uploaded file
    if uploaded_file and uploaded_file.filename:
        saved_path = _save_upload(uploaded_file)
        file_details['filename'] = uploaded_file.filename
        file_details['extension'] = saved_path.suffix.lower()

        try:
            extraction = extract_multimodal_content(saved_path, uploaded_file.filename, input_mode)
            extracted_text = extraction.get('text', '') or ''
            extraction_notes = extraction.get('notes', []) or []
            extraction_method = extraction.get('method', 'unknown')
            file_details.update(extraction.get('metadata', {}))
        finally:
            try:
                if saved_path.exists():
                    saved_path.unlink()
                if saved_path.parent.exists() and not any(saved_path.parent.iterdir()):
                    saved_path.parent.rmdir()
            except Exception:
                pass

    combined_context = extracted_text.strip()
    if not combined_context and question:
        combined_context = question

    related_topics = _build_related_topics(question or extracted_text[:120])

    # Step 2: Apply CRAG pipeline for fact-checked responses
    if is_gemini_configured():
        try:
            # Load vector database for retrieval
            config = get_config()
            index_path = f"{config.DATA_DIR}/faiss_index.bin"
            text_map_path = f"{config.DATA_DIR}/faiss_text_map.json"
            index, text_map = load_vector_db(index_path, text_map_path)
            
            # Execute CRAG pipeline
            crag_results = apply_crag(
                query=question or 'Analyze the uploaded material',
                index=index,
                text_map=text_map,
                extracted_text=extracted_text
            )
            
            # Build response with CRAG information
            return jsonify({
                'success': True,
                'mode': input_mode,
                'method': extraction_method,
                'metadata': file_details,
                'extracted_text': extracted_text,
                'notes': extraction_notes,
                'response': crag_results.get('final_response', ''),
                'related_topics': related_topics,
                # CRAG pipeline details
                'crag': {
                    'applied': crag_results.get('crag_applied', False),
                    'validation_passed': crag_results.get('validation_passed', True),
                    'confidence_score': crag_results.get('stage_3_validation', {}).get('confidence_score', 0),
                    'validation_issues': crag_results.get('stage_3_validation', {}).get('issues', []),
                    'stages_completed': 4
                }
            })
            
        except Exception as e:
            print(f"CRAG pipeline error: {str(e)}")
            # Fall back to basic generation if CRAG fails
            pass

    # Step 3: Fallback to non-CRAG response
    fallback = generate_multimodal_fallback_response(
        question=question or 'Uploaded material analysis',
        input_mode=input_mode,
        extracted_text=combined_context,
        file_metadata=file_details,
        notes=extraction_notes,
        related_topics=related_topics,
    )

    return jsonify({
        'success': True,
        'mode': input_mode,
        'method': extraction_method,
        'metadata': file_details,
        'extracted_text': extracted_text,
        'notes': extraction_notes,
        'response': fallback,
        'related_topics': related_topics,
        'fallback': True,
        'crag': {
            'applied': False,
            'validation_passed': False,
            'confidence_score': 0,
            'validation_issues': ['CRAG pipeline unavailable, using fallback response'],
            'stages_completed': 0
        }
    })