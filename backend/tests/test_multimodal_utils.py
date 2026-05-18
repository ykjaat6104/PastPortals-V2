"""
Unit tests for multimodal utilities
"""
import io
import os
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import pytest

from utils.multimodal_utils import (
    extract_multimodal_content,
    generate_multimodal_fallback_response,
    generate_multimodal_prompt,
    summarize_keywords,
    _read_text_file,
    _extract_pdf_text,
    _extract_docx_text,
    _ocr_image,
    _sample_video_frames,
    _extract_video_text,
)


class TestTextFileExtraction(TestCase):
    """Test plain text file extraction"""
    
    def test_read_text_file_utf8(self):
        """Test reading UTF-8 encoded text file"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write('Hello, World!\nThis is a test.')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            content = _read_text_file(temp_path)
            assert content == 'Hello, World!\nThis is a test.'
        finally:
            temp_path.unlink()
    
    def test_read_text_file_empty(self):
        """Test reading empty text file"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write('')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            content = _read_text_file(temp_path)
            assert content == ''
        finally:
            temp_path.unlink()
    
    def test_read_text_file_nonexistent(self):
        """Test reading non-existent file returns empty string"""
        content = _read_text_file(Path('/nonexistent/path.txt'))
        assert content == ''


class TestMultimodalContentExtraction(TestCase):
    """Test multimodal content extraction"""
    
    def test_extract_text_file(self):
        """Test extracting text from plain text file"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write('Test document content')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            result = extract_multimodal_content(str(temp_path), 'test.txt', 'document')
            assert result['text'] == 'Test document content'
            assert result['method'] == 'text-file'
            assert 'notes' in result
            assert 'metadata' in result
            assert result['metadata']['filename'] == 'test.txt'
        finally:
            temp_path.unlink()
    
    def test_extract_markdown_file(self):
        """Test extracting markdown file"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.md') as f:
            f.write('# Heading\n\nContent here')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            result = extract_multimodal_content(str(temp_path), 'test.md')
            assert '# Heading' in result['text']
            assert result['method'] == 'text-file'
        finally:
            temp_path.unlink()
    
    def test_extract_json_file(self):
        """Test extracting JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as f:
            f.write('{"key": "value", "name": "test"}')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            result = extract_multimodal_content(str(temp_path), 'test.json')
            assert 'key' in result['text']
            assert result['method'] == 'text-file'
        finally:
            temp_path.unlink()


class TestMultimodalPromptGeneration(TestCase):
    """Test multimodal prompt generation"""
    
    def test_generate_document_prompt(self):
        """Test generating prompt for document analysis"""
        prompt = generate_multimodal_prompt(
            question='What is this document about?',
            input_mode='document',
            extracted_text='This is a historical document from 1850.',
            file_metadata={'filename': 'doc.txt', 'size_bytes': 1024}
        )
        assert 'document' in prompt.lower()
        assert 'historical document' in prompt
        assert '900-1100 words' in prompt or '1100 words' in prompt
    
    def test_generate_image_prompt(self):
        """Test generating prompt for image analysis"""
        prompt = generate_multimodal_prompt(
            question='Describe this image',
            input_mode='image',
            extracted_text='Text from image OCR'
        )
        assert 'image' in prompt.lower()
        assert 'visible text' in prompt.lower() or 'symbols' in prompt.lower()
    
    def test_generate_video_prompt(self):
        """Test generating prompt for video analysis"""
        prompt = generate_multimodal_prompt(
            question='What happens in this video?',
            input_mode='video',
            extracted_text='Frame text: ...'
        )
        assert 'video' in prompt.lower()
        assert 'frame' in prompt.lower() or 'sampled' in prompt.lower()
    
    def test_prompt_includes_metadata(self):
        """Test that prompt includes file metadata"""
        metadata = {'filename': 'test.pdf', 'extension': '.pdf', 'size_bytes': 5000}
        prompt = generate_multimodal_prompt(
            question='Test',
            input_mode='document',
            file_metadata=metadata
        )
        assert 'test.pdf' in prompt or 'pdf' in prompt.lower()


class TestMultimodalFallbackResponse(TestCase):
    """Test fallback response generation"""
    
    def test_fallback_response_structure(self):
        """Test that fallback response has required sections"""
        response = generate_multimodal_fallback_response(
            question='What is this?',
            input_mode='document',
            extracted_text='Sample extracted text'
        )
        assert '## Multimodal Analysis' in response
        assert '### Overview' in response
        assert '### Extracted Content' in response or 'Extracted Content' in response
        assert '### Historical Context' in response
    
    def test_fallback_response_with_empty_text(self):
        """Test fallback response when no text was extracted"""
        response = generate_multimodal_fallback_response(
            question='Test question',
            input_mode='image',
            extracted_text=''
        )
        assert 'No readable text' in response or 'extracted' in response.lower()
        assert '### Historical Context' in response
    
    def test_fallback_response_with_metadata(self):
        """Test fallback includes metadata info"""
        metadata = {
            'filename': 'test.mp4',
            'frame_count': 120,
            'sampled_frames': 8,
            'duration_seconds': 5.0
        }
        response = generate_multimodal_fallback_response(
            question='Video test',
            input_mode='video',
            extracted_text='Frame text',
            file_metadata=metadata
        )
        assert 'test.mp4' in response or 'mp4' in response.lower()
        assert '120' in response or 'frame' in response.lower()


class TestKeywordSummarization(TestCase):
    """Test keyword summarization"""
    
    def test_summarize_keywords_basic(self):
        """Test basic keyword extraction"""
        text = 'history historical museum ancient Egypt pyramids pharaoh Nile river'
        keywords = summarize_keywords(text, limit=5)
        assert len(keywords) <= 5
        assert isinstance(keywords, list)
        assert all(isinstance(k, str) for k in keywords)
    
    def test_summarize_keywords_filters_short(self):
        """Test that short words are filtered out"""
        text = 'a an the history museum ancient Egypt'
        keywords = summarize_keywords(text, limit=10)
        # Should filter words with 3 chars or less
        assert all(len(k) > 3 for k in keywords)
    
    def test_summarize_keywords_limit(self):
        """Test that keyword limit is respected"""
        text = 'word1 word2 word3 word4 word5 word6 word7 word8 word9 word10'
        keywords = summarize_keywords(text, limit=3)
        assert len(keywords) <= 3
    
    def test_summarize_keywords_empty_text(self):
        """Test with empty text"""
        keywords = summarize_keywords('', limit=5)
        assert keywords == []


class TestMetadataHandling(TestCase):
    """Test metadata extraction and handling"""
    
    def test_metadata_file_size(self):
        """Test file size is captured in metadata"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            f.write(b'A' * 1024)  # 1 KB
            f.flush()
            temp_path = Path(f.name)
        
        try:
            result = extract_multimodal_content(str(temp_path), 'test.txt')
            assert result['metadata']['size_bytes'] == 1024
        finally:
            temp_path.unlink()
    
    def test_metadata_extension(self):
        """Test file extension is captured"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            f.write(b'{"test": true}')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            result = extract_multimodal_content(str(temp_path), 'test.json')
            assert result['metadata']['extension'] == '.json'
        finally:
            temp_path.unlink()
    
    def test_metadata_mode(self):
        """Test input mode is preserved"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            f.write(b'test')
            f.flush()
            temp_path = Path(f.name)
        
        try:
            result = extract_multimodal_content(str(temp_path), 'test.txt', 'document')
            assert result['metadata']['mode'] == 'document'
        finally:
            temp_path.unlink()


class TestErrorHandling(TestCase):
    """Test error handling in multimodal processing"""
    
    def test_extract_nonexistent_file(self):
        """Test extracting from nonexistent file"""
        # Should not raise, but return generic text extraction
        result = extract_multimodal_content('/nonexistent/file.txt')
        assert 'text' in result
        assert 'notes' in result
    
    def test_fallback_with_notes(self):
        """Test fallback response includes processing notes"""
        notes = ['OCR failed', 'PDF extraction skipped']
        response = generate_multimodal_fallback_response(
            question='Test',
            input_mode='image',
            notes=notes
        )
        assert 'Processing notes' in response or 'notes' in response.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
