"""
Flickr data collection module for Pegasus-Bazooka OSINT tool.
"""

import flickrapi
import json
import time
import config
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def authenticate():
    """
    Authenticate with Flickr API.
    
    Returns:
        flickrapi.FlickrAPI: Authenticated API object
    """
    try:
        flickr = flickrapi.FlickrAPI(
            config.API_KEYS['flickr']['api_key'],
            config.API_KEYS['flickr']['api_secret'],
            format='parsed-json'
        )
        return flickr
    except Exception as e:
        print(f"Flickr authentication error: {e}")
        return None
        
def search_by_location(latitude, longitude, radius_km, max_results=100, since_days=30):
    """
    Search Flickr for geotagged photos near a location.
    
    Args:
        latitude (float): Center latitude
        longitude (float): Center longitude
        radius_km (float): Search radius in kilometers
        max_results (int): Maximum number of results to return
        since_days (int): Get photos from the last X days
        
    Returns:
        list: List of photo data
    """
    flickr = authenticate()
    if not flickr:
        return []
        
    # Calculate min/max upload date
    min_date = datetime.now() - timedelta(days=since_days)
    min_date_unix = int(min_date.timestamp())
    
    results = []
    try:
        # Search for photos
        response = flickr.photos.search(
            lat=latitude,
            lon=longitude,
            radius=radius_km,
            radius_units='km',
            has_geo=1,
            extras='geo,url_m,date_taken,description,owner_name,tags',
            per_page=min(max_results, 500),  # Max allowed by API
            page=1,
            min_upload_date=min_date_unix,
            sort='date-taken-desc'
        )
        
        if 'photos' in response and 'photo' in response['photos']:
            for photo in response['photos']['photo']:
                results.append(photo)
                
                # Respect rate limits
                time.sleep(config.REQUEST_DELAY)
                
                # Stop if we have enough results
                if len(results) >= max_results:
                    break
    
    except Exception as e:
        print(f"Flickr search error: {e}")
        
    return results
    
def search_by_keyword(keyword, max_results=100, since_days=30):
    """
    Search Flickr for photos with a specific keyword.
    
    Args:
        keyword (str): Keyword to search for
        max_results (int): Maximum number of results to return
        since_days (int): Get photos from the last X days
        
    Returns:
        list: List of photo data
    """
    flickr = authenticate()
    if not flickr:
        return []
        
    # Calculate min/max upload date
    min_date = datetime.now() - timedelta(days=since_days)
    min_date_unix = int(min_date.timestamp())
    
    results = []
    try:
        # Search for photos
        response = flickr.photos.search(
            text=keyword,
            has_geo=1,
            extras='geo,url_m,date_taken,description,owner_name,tags',
            per_page=min(max_results, 500),  # Max allowed by API
            page=1,
            min_upload_date=min_date_unix,
            sort='relevance'
        )
        
        if 'photos' in response and 'photo' in response['photos']:
            for photo in response['photos']['photo']:
                results.append(photo)
                
                # Respect rate limits
                time.sleep(config.REQUEST_DELAY)
                
                # Stop if we have enough results
                if len(results) >= max_results:
                    break
    
    except Exception as e:
        print(f"Flickr search error: {e}")
        
    return results
    
def get_photo_info(photo_id):
    """
    Get detailed information about a specific photo.
    
    Args:
        photo_id (str): Flickr photo ID
        
    Returns:
        dict: Photo information
    """
    flickr = authenticate()
    if not flickr:
        return {}
        
    try:
        # Get photo info
        response = flickr.photos.getInfo(photo_id=photo_id)
        return response['photo'] if 'photo' in response else {}
    
    except Exception as e:
        print(f"Flickr photo info error: {e}")
        return {}
        
def scrape_without_api(keyword=None, max_results=20):
    """
    Scrape Flickr without API (fallback method).
    
    Args:
        keyword (str): Optional keyword to search for
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of photo data
    """
    import requests
    from bs4 import BeautifulSoup
    
    results = []
    
    # Set up session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': config.USER_AGENT,
        'Accept-Language': 'en-US,en;q=0.9'
    })
    
    try:
        # Build URL
        url = 'https://www.flickr.com/search/'
        params = {
            'text': f"{keyword if keyword else ''} geotagged",
            'view_all': '1'
        }
        
        # Make request
        response = session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find photos
            photos = soup.find_all('div', {'class': 'photo-list-photo-view'})
            
            for photo in photos[:max_results]:
                # Basic extraction of photo data
                photo_data = {}
                
                # Get photo ID and src
                if 'data-id' in photo.attrs:
                    photo_data['id'] = photo['data-id']
                    
                # Try to get image URL
                img = photo.find('img')
                if img and 'src' in img.attrs:
                    photo_data['url_m'] = img['src']
                    
                # Try to get title
                if 'title' in photo.attrs:
                    photo_data['title'] = photo['title']
                    
                # Append to results if we have at least an ID
                if 'id' in photo_data:
                    results.append(photo_data)
                    
                # Respect rate limits
                time.sleep(config.REQUEST_DELAY)
    
    except Exception as e:
        print(f"Flickr scraping error: {e}")
    
    return results 