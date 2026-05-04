import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import VoiceSearchBar from './VoiceSearchBar';
import { useAPI } from '../contexts/APIContext';
import { useLocation } from 'react-router-dom';
import { getTopicImages } from '../utils/imageSearch';
import { useLocalStorage } from '../hooks/useCustomHooks';

const SearchPageNew = () => {
  const { askQuestion, language } = useAPI();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResult, setSearchResult] = useState('');
  const [searchData, setSearchData] = useState(null);
  const [searching, setSearching] = useState(false);
  const [images, setImages] = useState([]);
  const [searchHistory, setSearchHistory] = useLocalStorage('searchHistory', []);
  const [historyPanelOpen, setHistoryPanelOpen] = useState(true);
  const [historyVisibleCount, setHistoryVisibleCount] = useState(10);
  const activeSearchId = useRef(0);
  const historyListRef = useRef(null);
  const historyLoadMoreRef = useRef(null);

  const normalizeQuery = (value) => value.trim().replace(/\s+/g, ' ').toLowerCase();

  const sanitizeAnswerText = (text) => {
    if (!text) {
      return '';
    }

    return text
      .split('\n')
      .filter((line) => {
        const normalizedLine = line.trim().toLowerCase();
        if (!normalizedLine) {
          return true;
        }

        if (normalizedLine.startsWith('source:')) {
          return false;
        }

        if (normalizedLine.startsWith('**source:**')) {
          return false;
        }

        if (normalizedLine.includes('[wikipedia](')) {
          return false;
        }

        return true;
      })
      .join('\n')
      .trim();
  };

  const saveSearchToHistory = (query, responseData, answerText, resultImages) => {
    const entry = {
      query,
      normalizedQuery: normalizeQuery(query),
      answer: sanitizeAnswerText(answerText),
      data: responseData,
      images: resultImages,
      source: responseData?.source || 'unknown',
      timestamp: new Date().toISOString()
    };

    setSearchHistory((previousHistory) => {
      const nextHistory = [
        entry,
        ...(Array.isArray(previousHistory) ? previousHistory.filter((item) => item.normalizedQuery !== entry.normalizedQuery) : [])
      ];

      return nextHistory.slice(0, 50);
    });
  };

  const getCachedSearch = (query) => {
    const normalizedQuery = normalizeQuery(query);
    return Array.isArray(searchHistory)
      ? searchHistory.find((item) => item.normalizedQuery === normalizedQuery)
      : null;
  };

  const applyCachedSearch = (cachedEntry) => {
    if (!cachedEntry) {
      return false;
    }

    // Re-fetch non-AI cached entries so users are not stuck with
    // old, short fallback responses after backend improvements.
    if (cachedEntry.source !== 'ai') {
      return false;
    }

    activeSearchId.current += 1;
    setSearchQuery(cachedEntry.query);
    setSearchResult(sanitizeAnswerText(cachedEntry.answer || ''));
    setSearchData(cachedEntry.data || null);
    setImages(Array.isArray(cachedEntry.images) ? cachedEntry.images : []);
    setSearching(false);
    return true;
  };

  useEffect(() => {
    const incomingQuery = location.state?.query || location.state?.searchQuery;
    const shouldAutoSearch = location.state?.autoSearch !== false; // Default to true
    
    if (incomingQuery) {
      setSearchQuery(incomingQuery);
      if (shouldAutoSearch) {
        handleAutoSearch(incomingQuery);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  useEffect(() => {
    if (historyPanelOpen) {
      setHistoryVisibleCount((currentCount) => Math.max(currentCount, 10));
    }
  }, [historyPanelOpen]);

  useEffect(() => {
    if (!historyPanelOpen) {
      return;
    }

    if (historyVisibleCount > searchHistory.length) {
      setHistoryVisibleCount(searchHistory.length);
    }
  }, [historyPanelOpen, historyVisibleCount, searchHistory.length]);

  useEffect(() => {
    if (!historyPanelOpen || historyVisibleCount >= searchHistory.length) {
      return;
    }

    const scrollContainer = historyListRef.current;
    const loadMoreTrigger = historyLoadMoreRef.current;

    if (!scrollContainer || !loadMoreTrigger) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setHistoryVisibleCount((currentCount) => Math.min(currentCount + 10, searchHistory.length));
        }
      },
      {
        root: scrollContainer,
        rootMargin: '120px',
        threshold: 0.1
      }
    );

    observer.observe(loadMoreTrigger);

    return () => observer.disconnect();
  }, [historyPanelOpen, historyVisibleCount, searchHistory.length]);

  const handleAutoSearch = async (query) => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      return;
    }

    const cachedEntry = getCachedSearch(trimmedQuery);
    if (applyCachedSearch(cachedEntry)) {
      return;
    }

    const searchId = activeSearchId.current + 1;
    activeSearchId.current = searchId;

    setSearching(true);
    setSearchResult('');
    setSearchData(null);
    setImages([]);
    
    // Fetch images in parallel with text search.
    const imagePromise = getTopicImages(trimmedQuery, 3).then((imgs) => {
      if (activeSearchId.current === searchId) {
        setImages(imgs);
      }

      return imgs;
    });
    
    try {
      const response = await askQuestion(trimmedQuery);
      if (activeSearchId.current !== searchId) {
        return;
      }

      const fallbackText = response?.wikipedia_info?.extract || response?.message || '';
      const answerText = sanitizeAnswerText(response?.answer || response?.response || fallbackText);
      const loadedImages = await imagePromise.catch(() => []);

      if (!answerText) {
        throw new Error('No search content returned from backend');
      }

      setSearchData(response);
      setSearchResult(answerText);
      saveSearchToHistory(trimmedQuery, response, answerText, loadedImages);
    } catch (error) {
      if (activeSearchId.current !== searchId) {
        return;
      }

      console.error('Search error:', error);
      const errorMsg = `Error: ${error.message || 'Search failed'}

Troubleshooting:
• Check browser console (F12) for details
    • Verify backend is running on port 5000
    • Verify internet connection
    • CORS origin allowed: ${window.location.origin}
    • API Key: ${(error.message || '').includes('API') ? 'Issue with Gemini API' : 'Connection or server issue'}`;
      setSearchResult(errorMsg);
    } finally {
      if (activeSearchId.current === searchId) {
        setSearching(false);
      }
    }
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    await handleAutoSearch(searchQuery);
  };

  const handleHistoryClick = (query) => {
    setSearchQuery(query);
    handleAutoSearch(query);
  };

  const clearSearchHistory = () => {
    setSearchHistory([]);
    setHistoryVisibleCount(10);
  };

  const suggestions = [
    { icon: '🏛️', text: 'Ancient Rome', gradient: 'from-red-500 to-purple-600' },
    { icon: '🗿', text: 'Egyptian Pyramids', gradient: 'from-yellow-500 to-orange-600' },
    { icon: '🏺', text: 'Greek Mythology', gradient: 'from-blue-500 to-cyan-500' },
    { icon: '🕌', text: 'Mughal Empire', gradient: 'from-orange-500 to-pink-600' },
    { icon: '⚔️', text: 'Medieval Europe', gradient: 'from-gray-600 to-blue-700' },
    { icon: '🎭', text: 'Renaissance Art', gradient: 'from-purple-500 to-pink-500' }
  ];

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    handleAutoSearch(suggestion);
  };

  const answerText = searchData?.answer || searchData?.response || searchResult;

  const getLanguageName = (code) => {
    const names = {
      en: 'English', hi: 'हिन्दी', fr: 'Français', es: 'Español',
      pt: 'Português', ar: 'العربية', zh: '中文', ja: '日本語',
      de: 'Deutsch', it: 'Italiano', ru: 'Русский', ko: '한국어'
    };
    return names[code] || 'English';
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <h1 className="page-title">
          <Search size={36} />
          Search History
        </h1>
        <p className="page-subtitle">
          Ask questions about any historical topic, event, or civilization
          <span style={{ marginLeft: '12px', padding: '4px 12px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '12px', fontSize: '0.85em', fontWeight: '600', color: '#6366f1' }}>
            {getLanguageName(language)}
          </span>
        </p>
      </div>

      <div className="search-bar-container">
        <VoiceSearchBar
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onSubmit={handleSearch}
          placeholder="Search for historical topics, events, people..."
          className="main-search-bar"
        />
      </div>

      {searchHistory.length > 0 && (
        <div className="history-panel">
          <div className="history-panel-header">
            <div>
              <h2>Search history</h2>
              <p>{searchHistory.length} saved searches ready to reopen</p>
            </div>
            <div className="history-panel-actions">
              <button
                type="button"
                className="source-link"
                onClick={() => setHistoryPanelOpen((open) => !open)}
              >
                {historyPanelOpen ? 'Hide history' : 'Show history'}
              </button>
              <button type="button" className="source-link" onClick={clearSearchHistory}>
                Clear history
              </button>
            </div>
          </div>

          {historyPanelOpen && (
            <div ref={historyListRef} className="history-panel-body">
              <div className="suggestions-grid history-grid">
                {searchHistory.slice(0, historyVisibleCount).map((item) => (
                  <button
                    key={`${item.normalizedQuery}-${item.timestamp}`}
                    className="suggestion-card history-card"
                    onClick={() => handleHistoryClick(item.query)}
                  >
                    <div className="suggestion-content">
                      <span className="suggestion-text">{item.query}</span>
                      <span className="suggestion-category">
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </button>
                ))}
              </div>

              {historyVisibleCount < searchHistory.length && (
                <div ref={historyLoadMoreRef} className="history-load-more">
                  <span>Scroll for older searches</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {!searchResult && (
        <div className="suggestions-section">
          <h2 className="section-title">
            <Sparkles size={20} />
            Popular Topics
          </h2>
          <div className="suggestions-grid">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                className="suggestion-card"
                onClick={() => handleSuggestionClick(suggestion.text)}
              >
                <div className={`suggestion-icon bg-gradient-to-br ${suggestion.gradient}`}>
                  <span>{suggestion.icon}</span>
                </div>
                <span className="suggestion-text">{suggestion.text}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {searching && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>🔍 Searching through history with AI...</p>
          <small>Powered by Google Gemini</small>
        </div>
      )}

      {searchResult && (
        <div className="search-results">
          <div className="result-header">
            <h2>Search Results</h2>
            <span className="result-badge">AI-Powered</span>
          </div>

          <div className="answer-section-wikipedia">
            <h3 className="section-title">
              <Sparkles size={22} />
              {searchQuery}
            </h3>
            
            <div className="wiki-content">
              {/* Wikipedia-style layout with text wrapping around images */}
              <div className="wiki-article">
                {/* Images float on the right side */}
                {images.length > 0 && images.map((img, idx) => (
                  <figure key={idx} className="wiki-infobox">
                    <img 
                      src={img.url} 
                      alt={img.title}
                      loading="lazy"
                    />
                    <figcaption>{img.title}</figcaption>
                  </figure>
                ))}
                
                {/* Text content flows around the images */}
                <div className="wiki-text">
                  <ReactMarkdown>{answerText}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>

          {searchData?.museum_data?.smithsonian?.length > 0 && (
            <div className="source-info" style={{ alignItems: 'flex-start', flexDirection: 'column', gap: '12px' }}>
              <span>Related museum artifacts</span>
              <span>{searchData.museum_data.total_count} museum artifacts found</span>
              <div style={{ display: 'grid', gap: '10px', width: '100%' }}>
                {searchData.museum_data.smithsonian.map((artifact, idx) => (
                  <div key={idx} style={{ padding: '12px', borderRadius: '12px', background: 'rgba(255,255,255,0.04)' }}>
                    <strong>{artifact.title}</strong>
                    <div>{artifact.type}</div>
                    <a href={artifact.url} target="_blank" rel="noreferrer">Open artifact</a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchPageNew;
