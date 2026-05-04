/**
 * Unit tests for MultimodalPanel component
 * Using Jest and React Testing Library
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { toast } from 'react-hot-toast';
import MultimodalPanel from '../components/MultimodalPanel';
import * as apiService from '../utils/api';

// Mock dependencies
jest.mock('react-hot-toast');
jest.mock('../utils/api');
jest.mock('../components/VoiceSearchBar', () => {
  return function DummyVoiceSearchBar() {
    return <div data-testid="voice-search-bar">Voice Search Bar</div>;
  };
});

describe('MultimodalPanel Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock default API response
    apiService.apiService = {
      analyzeMultimodal: jest.fn(() =>
        Promise.resolve({
          success: true,
          extracted_text: 'Sample extracted text',
          response: 'Generated response',
          notes: [],
          metadata: { filename: 'test.txt', extension: '.txt', mode: 'document' },
          fallback: false,
        })
      ),
    };
  });

  describe('Rendering', () => {
    test('renders multimodal panel with all mode options', () => {
      render(<MultimodalPanel />);
      
      expect(screen.getByText('Multimodal analysis studio')).toBeInTheDocument();
      expect(screen.getByText('Document')).toBeInTheDocument();
      expect(screen.getByText('Image')).toBeInTheDocument();
      expect(screen.getByText('Video')).toBeInTheDocument();
      expect(screen.getByText('Voice')).toBeInTheDocument();
    });

    test('renders document mode by default', () => {
      render(<MultimodalPanel />);
      
      expect(screen.getByText('Document upload')).toBeInTheDocument();
      expect(screen.getByText(/PDF, DOCX, TXT/)).toBeInTheDocument();
    });

    test('renders research question textarea', () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      expect(textarea).toBeInTheDocument();
    });

    test('renders analyze and clear buttons', () => {
      render(<MultimodalPanel />);
      
      expect(screen.getByRole('button', { name: /Analyze input/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Clear/i })).toBeInTheDocument();
    });
  });

  describe('Mode Switching', () => {
    test('switches to image mode', () => {
      render(<MultimodalPanel />);
      
      const imageBtn = screen.getAllByRole('button').find(btn => 
        btn.textContent.includes('Image') && !btn.textContent.includes('Max')
      );
      fireEvent.click(imageBtn);
      
      expect(screen.getByText('Image OCR')).toBeInTheDocument();
      expect(screen.getByText(/photos, screenshots/i)).toBeInTheDocument();
    });

    test('switches to video mode', () => {
      render(<MultimodalPanel />);
      
      const videoBtn = screen.getAllByRole('button').find(btn => 
        btn.textContent.includes('Video') && !btn.textContent.includes('Max')
      );
      fireEvent.click(videoBtn);
      
      expect(screen.getByText('Video analysis')).toBeInTheDocument();
    });

    test('switches to voice mode', () => {
      render(<MultimodalPanel />);
      
      const voiceBtn = screen.getAllByRole('button').find(btn => 
        btn.textContent === 'Voice'
      );
      fireEvent.click(voiceBtn);
      
      expect(screen.getByTestId('voice-search-bar')).toBeInTheDocument();
    });

    test('clears selection when switching modes', () => {
      render(<MultimodalPanel />);
      
      // Set a question
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test question' } });
      
      // Switch mode
      const imageBtn = screen.getAllByRole('button').find(btn => 
        btn.textContent.includes('Image') && !btn.textContent.includes('Max')
      );
      fireEvent.click(imageBtn);
      
      // Question should be cleared
      const newTextarea = screen.getByPlaceholderText(/Ask what this document/);
      expect(newTextarea.value).toBe('');
    });
  });

  describe('File Validation', () => {
    test('shows error for oversized document', async () => {
      render(<MultimodalPanel />);
      
      const file = new File(['a'.repeat(60 * 1024 * 1024 + 1)], 'large.txt', { type: 'text/plain' });
      const input = screen.getByDisplayValue('') || document.querySelector('input[type="file"]');
      
      // Simulate file selection
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/exceeds limit/i)).toBeInTheDocument();
      });
    });

    test('shows error for unsupported file format in document mode', async () => {
      render(<MultimodalPanel />);
      
      const file = new File(['content'], 'test.exe', { type: 'application/x-msdownload' });
      const input = document.querySelector('input[type="file"]');
      
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/File format not supported/i)).toBeInTheDocument();
      });
    });

    test('accepts valid document formats', async () => {
      render(<MultimodalPanel />);
      
      const validFormats = ['test.pdf', 'test.docx', 'test.txt', 'test.md'];
      for (const filename of validFormats) {
        const file = new File(['content'], filename, { type: 'application/octet-stream' });
        const input = document.querySelector('input[type="file"]');
        
        Object.defineProperty(input, 'files', {
          value: [file],
        });
        fireEvent.change(input);
        
        // Should not show validation error
        await waitFor(() => {
          const errors = screen.queryAllByText(/File validation failed/i);
          expect(errors.length).toBe(0);
        });
      }
    });
  });

  describe('File Display', () => {
    test('displays file name after selection', async () => {
      render(<MultimodalPanel />);
      
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]');
      
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/test.txt/)).toBeInTheDocument();
      });
    });

    test('displays file size in human-readable format', async () => {
      render(<MultimodalPanel />);
      
      // Create a 1 KB file
      const file = new File(['a'.repeat(1024)], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]');
      
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/KB/i)).toBeInTheDocument();
      });
    });
  });

  describe('Question Input', () => {
    test('accepts text input in question field', () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'What is this about?' } });
      
      expect(textarea.value).toBe('What is this about?');
    });

    test('allows empty question for file-only analysis', () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      expect(textarea.value).toBe('');
      
      // Analyze button should not complain about empty question if file is present
      expect(screen.getByRole('button', { name: /Analyze input/i })).toBeInTheDocument();
    });
  });

  describe('Analysis', () => {
    test('calls API with form data on analyze', async () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test question' } });
      
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]');
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      await waitFor(() => {
        expect(apiService.apiService.analyzeMultimodal).toHaveBeenCalled();
      });
    });

    test('shows loading state during analysis', async () => {
      apiService.apiService.analyzeMultimodal.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          success: true,
          extracted_text: 'text',
          response: 'response',
          metadata: {},
          notes: [],
        }), 100))
      );
      
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      expect(screen.getByRole('button', { name: /Analyzing/i })).toBeInTheDocument();
    });

    test('displays analysis results', async () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      await waitFor(() => {
        expect(screen.getByText('Analysis output')).toBeInTheDocument();
        expect(screen.getByText('Sample extracted text')).toBeInTheDocument();
      });
    });

    test('shows success toast on successful analysis', async () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      await waitFor(() => {
        expect(toast.success).toHaveBeenCalled();
      });
    });

    test('shows error message on API failure', async () => {
      apiService.apiService.analyzeMultimodal.mockRejectedValue(new Error('API Error'));
      
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      await waitFor(() => {
        expect(screen.getByText('API Error')).toBeInTheDocument();
        expect(toast.error).toHaveBeenCalled();
      });
    });
  });

  describe('Clear Functionality', () => {
    test('clears all fields when clear button is clicked', async () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test question' } });
      
      const clearBtn = screen.getByRole('button', { name: /Clear/i });
      fireEvent.click(clearBtn);
      
      expect(textarea.value).toBe('');
    });

    test('removes error messages when clear is clicked', async () => {
      render(<MultimodalPanel />);
      
      // Create a validation error
      const file = new File(['a'.repeat(60 * 1024 * 1024 + 1)], 'large.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]');
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/exceeds limit/i)).toBeInTheDocument();
      });
      
      const clearBtn = screen.getByRole('button', { name: /Clear/i });
      fireEvent.click(clearBtn);
      
      await waitFor(() => {
        const errors = screen.queryAllByText(/exceeds limit/i);
        expect(errors.length).toBe(0);
      });
    });
  });

  describe('File Size Formatting', () => {
    test('formats bytes correctly', async () => {
      render(<MultimodalPanel />);
      
      const file = new File(['a'.repeat(1024)], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]');
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/1\s*KB/i)).toBeInTheDocument();
      });
    });

    test('formats megabytes correctly', async () => {
      render(<MultimodalPanel />);
      
      const file = new File(['a'.repeat(1024 * 1024)], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]');
      Object.defineProperty(input, 'files', {
        value: [file],
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText(/1\s*MB/i)).toBeInTheDocument();
      });
    });
  });

  describe('Metadata Display', () => {
    test('displays file metadata in results', async () => {
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      await waitFor(() => {
        expect(screen.getByText('test.txt')).toBeInTheDocument();
      });
    });

    test('displays analysis notes', async () => {
      apiService.apiService.analyzeMultimodal.mockResolvedValue({
        success: true,
        extracted_text: 'text',
        response: 'response',
        notes: ['Note 1', 'Note 2'],
        metadata: { filename: 'test.txt', extension: '.txt', mode: 'document' },
        fallback: false,
      });
      
      render(<MultimodalPanel />);
      
      const textarea = screen.getByPlaceholderText(/Ask what this document/);
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      const analyzeBtn = screen.getByRole('button', { name: /Analyze input/i });
      fireEvent.click(analyzeBtn);
      
      await waitFor(() => {
        expect(screen.getByText('Processing notes')).toBeInTheDocument();
        expect(screen.getByText('Note 1')).toBeInTheDocument();
        expect(screen.getByText('Note 2')).toBeInTheDocument();
      });
    });
  });
});

describe('File Validation Utility Functions', () => {
  test('validates file size limits', () => {
    // This would test the validateFile function if exported
    // For now, we test through the component
  });

  test('validates file format restrictions', () => {
    // This would test the validateFile function if exported
    // For now, we test through the component
  });
});
