"""
Wikipedia data collection module for Pegasus-Bazooka OSINT tool.
"""

import requests
import json
import time
import config
from datetime import datetime
import html

def get_nearby_articles(latitude, longitude, radius_km=10, limit=100, language='en'):
    """
    Get Wikipedia articles near a geographic location.
    
    Args:
        latitude (float): Center latitude
        longitude (float): Center longitude
        radius_km (float): Search radius in kilometers
        limit (int): Maximum number of results to return
        language (str): Wikipedia language code
        
    Returns:
        list: List of articles with geo information
    """
    # Convert radius to meters for the API
    radius_m = int(radius_km * 1000)
    
    # Set up session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': config.API_KEYS['wikipedia']['user_agent']
    })
    
    results = []
    try:
        # Build URL and parameters
        url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'geosearch',
            'gscoord': f"{latitude}|{longitude}",
            'gsradius': radius_m,
            'gslimit': limit,
            'format': 'json'
        }
        
        # Make request
        response = session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        data = response.json()
        
        if 'query' in data and 'geosearch' in data['query']:
            articles = data['query']['geosearch']
            
            # Process each article to get more info
            for article in articles:
                article_data = {
                    'title': article.get('title', ''),
                    'latitude': article.get('lat', None),
                    'longitude': article.get('lon', None),
                    'distance': article.get('dist', None),
                    'page_id': article.get('pageid', None)
                }
                
                # Get article extract to use as content
                article_data.update(get_article_extract(article['pageid'], language))
                
                results.append(article_data)
                
                # Respect rate limits
                time.sleep(config.REQUEST_DELAY)
    
    except Exception as e:
        print(f"Wikipedia nearby articles error: {e}")
    
    return results

def get_article_extract(page_id, language='en'):
    """
    Get extract/summary of a Wikipedia article.
    
    Args:
        page_id (int): Wikipedia page ID
        language (str): Wikipedia language code
        
    Returns:
        dict: Article extract and URL
    """
    # Set up session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': config.API_KEYS['wikipedia']['user_agent']
    })
    
    article_data = {
        'content': '',
        'url': '',
        'image_url': ''
    }
    
    try:
        # Build URL and parameters
        url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'prop': 'extracts|info|pageimages',
            'pageids': page_id,
            'exintro': 1,
            'explaintext': 1,
            'inprop': 'url',
            'pithumbsize': 500,
            'format': 'json'
        }
        
        # Make request
        response = session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        data = response.json()
        
        if 'query' in data and 'pages' in data['query'] and str(page_id) in data['query']['pages']:
            page = data['query']['pages'][str(page_id)]
            
            # Get extract
            if 'extract' in page:
                article_data['content'] = html.unescape(page['extract'])
            
            # Get URL
            if 'fullurl' in page:
                article_data['url'] = page['fullurl']
                
            # Get image
            if 'thumbnail' in page and 'source' in page['thumbnail']:
                article_data['image_url'] = page['thumbnail']['source']
    
    except Exception as e:
        print(f"Wikipedia article extract error: {e}")
    
    return article_data

def search_articles(keyword, limit=10, language='en'):
    """
    Search Wikipedia articles by keyword.
    
    Args:
        keyword (str): Keyword to search for
        limit (int): Maximum number of results to return
        language (str): Wikipedia language code
        
    Returns:
        list: List of articles
    """
    # Set up session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': config.API_KEYS['wikipedia']['user_agent']
    })
    
    results = []
    try:
        # Build URL and parameters
        url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': keyword,
            'srlimit': limit,
            'format': 'json'
        }
        
        # Make request
        response = session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        data = response.json()
        
        if 'query' in data and 'search' in data['query']:
            articles = data['query']['search']
            
            # Process each article
            for article in articles:
                article_data = {
                    'title': article.get('title', ''),
                    'page_id': article.get('pageid', None),
                    'snippet': html.unescape(article.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''))
                }
                
                # Check if the article has geo information
                geo_data = get_article_coordinates(article['pageid'], language)
                
                if geo_data.get('latitude') is not None and geo_data.get('longitude') is not None:
                    article_data.update(geo_data)
                    article_data.update(get_article_extract(article['pageid'], language))
                    results.append(article_data)
                
                # Respect rate limits
                time.sleep(config.REQUEST_DELAY)
    
    except Exception as e:
        print(f"Wikipedia search error: {e}")
    
    return results

def get_article_coordinates(page_id, language='en'):
    """
    Get geographic coordinates of a Wikipedia article if available.
    
    Args:
        page_id (int): Wikipedia page ID
        language (str): Wikipedia language code
        
    Returns:
        dict: Coordinates data
    """
    # Set up session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': config.API_KEYS['wikipedia']['user_agent']
    })
    
    geo_data = {
        'latitude': None,
        'longitude': None
    }
    
    try:
        # Build URL and parameters
        url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'prop': 'coordinates',
            'pageids': page_id,
            'format': 'json'
        }
        
        # Make request
        response = session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        data = response.json()
        
        if 'query' in data and 'pages' in data['query'] and str(page_id) in data['query']['pages']:
            page = data['query']['pages'][str(page_id)]
            
            if 'coordinates' in page and page['coordinates']:
                coord = page['coordinates'][0]
                geo_data['latitude'] = coord.get('lat')
                geo_data['longitude'] = coord.get('lon')
    
    except Exception as e:
        print(f"Wikipedia coordinates error: {e}")
    
    return geo_data 