"""
Unit tests for multimodal routes
"""
import io
import json
import tempfile
from pathlib import Path
from unittest import TestCase

import pytest

from backend.app import app


class TestMultimodalRoutes(TestCase):
    """Test multimodal API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
    
    def test_analyze_multimodal_text_file(self):
        """Test analyzing a plain text file"""
        data = {
            'question': 'What is this document about?',
            'mode': 'document',
            'file': (io.BytesIO(b'This is a historical document.'), 'test.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'extracted_text' in result
        assert 'response' in result
        assert 'metadata' in result
        assert result['metadata']['filename'] == 'test.txt'
    
    def test_analyze_multimodal_no_file_no_question(self):
        """Test request with no file and no question"""
        data = {
            'mode': 'document'
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False
        assert 'error' in result
    
    def test_analyze_multimodal_with_question_only(self):
        """Test analyzing with question but no file (voice mode)"""
        data = {
            'question': 'Tell me about ancient Egypt',
            'mode': 'voice'
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'response' in result
        assert result['mode'] == 'voice'
    
    def test_analyze_multimodal_metadata(self):
        """Test that metadata is properly returned"""
        file_content = b'Test document\nWith multiple lines\n'
        data = {
            'question': 'Test',
            'mode': 'document',
            'file': (io.BytesIO(file_content), 'document.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        result = json.loads(response.data)
        assert 'metadata' in result
        assert result['metadata']['filename'] == 'document.txt'
        assert result['metadata']['extension'] == '.txt'
        assert result['metadata']['mode'] == 'document'
        assert result['metadata']['size_bytes'] == len(file_content)
    
    def test_analyze_multimodal_extraction_method(self):
        """Test that extraction method is reported"""
        data = {
            'question': 'Test',
            'mode': 'document',
            'file': (io.BytesIO(b'Plain text'), 'test.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        result = json.loads(response.data)
        assert 'method' in result
        assert result['method'] in ['text-file', 'pdf', 'docx', 'ocr-image', 'ocr-video', 'generic-text']
    
    def test_analyze_multimodal_notes(self):
        """Test that processing notes are included"""
        data = {
            'question': 'Test',
            'mode': 'document',
            'file': (io.BytesIO(b'Content'), 'test.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        result = json.loads(response.data)
        assert 'notes' in result
        assert isinstance(result['notes'], list)
    
    def test_analyze_multimodal_fallback_flag(self):
        """Test that fallback flag is set when using fallback"""
        data = {
            'question': 'Test',
            'mode': 'document',
            'file': (io.BytesIO(b'Test'), 'test.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        result = json.loads(response.data)
        # fallback flag may or may not be present depending on Gemini availability
        # but if present, should be boolean
        if 'fallback' in result:
            assert isinstance(result['fallback'], bool)
    
    def test_analyze_multimodal_response_content(self):
        """Test that response contains meaningful content"""
        data = {
            'question': 'What is history?',
            'mode': 'voice'
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        result = json.loads(response.data)
        assert result['response']
        assert len(result['response']) > 50  # Should have substantial content
    
    def test_analyze_multimodal_related_topics(self):
        """Test that related topics are generated"""
        data = {
            'question': 'ancient rome',
            'mode': 'voice'
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        result = json.loads(response.data)
        # related_topics may be empty if no Wikipedia search succeeds
        assert 'related_topics' in result
        assert isinstance(result['related_topics'], list)


class TestMultimodalFileHandling(TestCase):
    """Test file handling in multimodal processing"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
    
    def test_file_cleanup_after_analysis(self):
        """Test that temporary files are cleaned up"""
        initial_temp_count = len(list(Path(tempfile.gettempdir()).glob('pastportals_multimodal_*')))
        
        data = {
            'question': 'Test',
            'mode': 'document',
            'file': (io.BytesIO(b'Test content'), 'test.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        
        # Allow a small delay for cleanup
        import time
        time.sleep(0.1)
        
        final_temp_count = len(list(Path(tempfile.gettempdir()).glob('pastportals_multimodal_*')))
        # Should not create permanent temp files
        assert final_temp_count <= initial_temp_count + 1  # Allow 1 for timing
    
    def test_different_file_types(self):
        """Test handling of various file types"""
        test_cases = [
            ('test.txt', b'Plain text content'),
            ('test.csv', b'col1,col2\nval1,val2'),
            ('test.json', b'{"key": "value"}'),
            ('test.md', b'# Markdown\n\nContent'),
        ]
        
        for filename, content in test_cases:
            data = {
                'question': 'Test',
                'mode': 'document',
                'file': (io.BytesIO(content), filename)
            }
            response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert result['metadata']['filename'] == filename


class TestMultimodalErrorScenarios(TestCase):
    """Test error handling in multimodal processing"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
    
    def test_analyze_multimodal_invalid_mode(self):
        """Test with invalid mode (should still work, treated as 'auto')"""
        data = {
            'question': 'Test',
            'mode': 'invalid_mode',
            'file': (io.BytesIO(b'Content'), 'test.txt')
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        # Should still process, treating invalid mode as 'auto'
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
    
    def test_analyze_multimodal_malformed_request(self):
        """Test malformed request"""
        response = self.client.post('/api/multimodal/analyze', data='invalid', content_type='text/plain')
        
        # Should return 400 or 415
        assert response.status_code in [400, 415]
    
    def test_analyze_multimodal_large_question(self):
        """Test with very large question text"""
        large_question = 'x' * 10000  # 10k characters
        data = {
            'question': large_question,
            'mode': 'voice'
        }
        response = self.client.post('/api/multimodal/analyze', data=data, content_type='multipart/form-data')
        
        # Should handle gracefully
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
