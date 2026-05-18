"""
Wikipedia API integration utilities
"""
import requests
from datetime import datetime

# User-Agent header required by Wikipedia API
HEADERS = {
    'User-Agent': 'AIMuseumGuide/1.0 (Educational Project; Python/3.x) requests/2.x'
}


def _build_wikipedia_url(title):
    return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"


def _normalize_query(query):
    clean_query = query or ''
    for prefix in ('tell me about', 'what is', 'who was', 'who is', 'explain the', 'give me'):
        clean_query = clean_query.replace(prefix, '')
    return clean_query.strip()

def search_wikipedia(query, limit=3):
    """
    Search Wikipedia for articles
    
    Args:
        query: Search query string
        limit: Number of results to return
        
    Returns:
        list: List of search results with title and snippet
    """
    try:
        clean_query = _normalize_query(query)
        
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': clean_query,
            'srlimit': limit
        }
        
        response = requests.get(search_url, params=search_params, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            for rank, item in enumerate(data.get('query', {}).get('search', [])[:limit], start=1):
                title = item.get('title', '')
                results.append({
                    'rank': rank,
                    'title': title,
                    'pageid': item.get('pageid'),
                    'snippet': item.get('snippet', ''),
                    'size': item.get('size'),
                    'wordcount': item.get('wordcount'),
                    'timestamp': item.get('timestamp'),
                    'url': _build_wikipedia_url(title) if title else '',
                })

            return results
        
        return []
        
    except Exception as e:
        print(f"Wikipedia search error: {str(e)}")
        return []

def get_wikipedia_summary(title):
    """
    Get Wikipedia page summary
    
    Args:
        title: Wikipedia page title
        
    Returns:
        dict: Summary data or None if error
    """
    try:
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        response = requests.get(summary_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title', ''),
                'extract': data.get('extract', ''),
                'description': data.get('description', ''),
                'thumbnail': data.get('thumbnail', {}).get('source', '') if data.get('thumbnail') else '',
                'url': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"Wikipedia summary error: {str(e)}")
        return None

def get_wikipedia_page_content(title, sections=None):
    """
    Get full Wikipedia page content
    
    Args:
        title: Wikipedia page title
        sections: List of section names to extract (optional)
        
    Returns:
        dict: Page content or None if error
    """
    try:
        content_url = "https://en.wikipedia.org/w/api.php"
        content_params = {
            'action': 'parse',
            'format': 'json',
            'page': title,
            'prop': 'text|sections',
            'disablelimitreport': True,
            'disableeditsection': True,
            'disabletoc': True
        }
        
        response = requests.get(content_url, params=content_params, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'parse' in data:
                return {
                    'title': data['parse']['title'],
                    'text': data['parse']['text']['*'],
                    'sections': data['parse'].get('sections', [])
                }
        
        return None
        
    except Exception as e:
        print(f"Wikipedia content error: {str(e)}")
        return None

def search_and_summarize(query):
    """
    Search Wikipedia and get summary of top result
    
    Args:
        query: Search query string
        
    Returns:
        dict: Summary data or None if error
    """
    try:
        # Search for articles
        search_results = search_wikipedia(query, limit=1)
        
        if not search_results:
            return None
        
        # Get summary of first result
        top_result = search_results[0]
        summary = get_wikipedia_summary(top_result['title']) or {}

        return {
            'query': query,
            'normalized_query': _normalize_query(query),
            'search_results': search_results,
            'top_result': top_result,
            'title': summary.get('title', top_result['title']),
            'extract': summary.get('extract', ''),
            'description': summary.get('description', ''),
            'thumbnail': summary.get('thumbnail', ''),
            'url': summary.get('url', top_result.get('url', '')),
            'timestamp': summary.get('timestamp', datetime.now().isoformat()),
        }
        
    except Exception as e:
        print(f"Wikipedia search and summarize error: {str(e)}")
        return None

def get_related_articles(title, limit=5):
    """
    Get related Wikipedia articles
    
    Args:
        title: Wikipedia page title
        limit: Number of related articles to return
        
    Returns:
        list: List of related article titles
    """
    try:
        related_url = "https://en.wikipedia.org/w/api.php"
        related_params = {
            'action': 'query',
            'format': 'json',
            'prop': 'links',
            'titles': title,
            'pllimit': limit
        }
        
        response = requests.get(related_url, params=related_params, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            related = []
            for page_id, page_data in pages.items():
                links = page_data.get('links', [])
                related.extend([link['title'] for link in links[:limit]])
            
            return related[:limit]
        
        return []
        
    except Exception as e:
        print(f"Wikipedia related articles error: {str(e)}")
        return []
