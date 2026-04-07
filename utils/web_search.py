"""
Web Search Utility for RAG System
Uses Google Custom Search API or DuckDuckGo as fallback
"""

import requests
from bs4 import BeautifulSoup
import os
from typing import List, Dict


def search_duckduckgo(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search using DuckDuckGo (no API key required)
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        List of search results with title, snippet, and url
    """
    try:
        # DuckDuckGo HTML search
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.post(url, data=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Parse search results
        for result in soup.find_all('div', class_='result', limit=max_results):
            try:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    if title and snippet:
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': link
                        })
            except Exception as e:
                continue
        
        return results
    
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []


def search_google_custom(query: str, api_key: str = None, cx: str = None, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search using Google Custom Search API
    
    Args:
        query: Search query
        api_key: Google API key
        cx: Custom Search Engine ID
        max_results: Maximum number of results
    
    Returns:
        List of search results
    """
    try:
        if not api_key or not cx:
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": max_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'url': item.get('link', '')
            })
        
        return results
    
    except Exception as e:
        print(f"Google search error: {e}")
        return []


def web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Main web search function - tries Google first, falls back to DuckDuckGo
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        List of search results
    """
    # Try Google Custom Search if API key is available
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cx = os.getenv("GOOGLE_CX")
    
    if google_api_key and google_cx:
        results = search_google_custom(query, google_api_key, google_cx, max_results)
        if results:
            return results
    
    # Fallback to DuckDuckGo
    return search_duckduckgo(query, max_results)


def format_search_results(results: List[Dict[str, str]]) -> str:
    """
    Format search results into a readable string
    
    Args:
        results: List of search results
    
    Returns:
        Formatted string
    """
    if not results:
        return "No web search results found."
    
    formatted = "WEB SEARCH RESULTS:\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"[Result {i}]\n"
        formatted += f"Title: {result['title']}\n"
        formatted += f"Content: {result['snippet']}\n"
        formatted += f"Source: {result['url']}\n\n"
    
    return formatted
