"""
Twitter data collection module for Pegasus-Bazooka OSINT tool.
"""

import tweepy
import time
import json
import config
from datetime import datetime, timedelta

def authenticate():
    """
    Authenticate with Twitter API.
    
    Returns:
        tweepy.API: Authenticated API object
    """
    try:
        auth = tweepy.OAuth1UserHandler(
            config.API_KEYS['twitter']['api_key'],
            config.API_KEYS['twitter']['api_secret'],
            config.API_KEYS['twitter']['access_token'],
            config.API_KEYS['twitter']['access_token_secret']
        )
        api = tweepy.API(auth)
        return api
    except Exception as e:
        print(f"Twitter authentication error: {e}")
        return None
        
def search_by_location(latitude, longitude, radius_km, max_results=100, since_days=7):
    """
    Search Twitter for geotagged tweets near a location.
    
    Args:
        latitude (float): Center latitude
        longitude (float): Center longitude
        radius_km (float): Search radius in kilometers
        max_results (int): Maximum number of results to return
        since_days (int): Get tweets from the last X days
        
    Returns:
        list: List of tweet data
    """
    api = authenticate()
    if not api:
        return []
        
    # Convert radius to miles (Twitter API uses miles)
    radius_mi = radius_km * 0.621371
    geocode = f"{latitude},{longitude},{radius_mi}mi"
    
    # Calculate since date
    since_date = datetime.now() - timedelta(days=since_days)
    since_str = since_date.strftime("%Y-%m-%d")
    
    results = []
    try:
        # Search for tweets
        tweets = tweepy.Cursor(
            api.search_tweets,
            q="",
            geocode=geocode,
            count=100,
            tweet_mode="extended",
            since=since_str,
            include_entities=True
        ).items(max_results)
        
        # Process tweets
        for tweet in tweets:
            tweet_data = tweet._json
            if tweet_data:
                results.append(tweet_data)
                
            # Respect rate limits
            time.sleep(config.REQUEST_DELAY)
            
    except tweepy.TweepyException as e:
        print(f"Twitter search error: {e}")
        
    return results
    
def search_by_keyword(keyword, max_results=100, since_days=7):
    """
    Search Twitter for tweets containing a keyword.
    
    Args:
        keyword (str): Keyword to search for
        max_results (int): Maximum number of results to return
        since_days (int): Get tweets from the last X days
        
    Returns:
        list: List of tweet data
    """
    api = authenticate()
    if not api:
        return []
        
    # Calculate since date
    since_date = datetime.now() - timedelta(days=since_days)
    since_str = since_date.strftime("%Y-%m-%d")
    
    results = []
    try:
        # Search for tweets
        tweets = tweepy.Cursor(
            api.search_tweets,
            q=keyword,
            count=100,
            tweet_mode="extended",
            since=since_str,
            include_entities=True
        ).items(max_results)
        
        # Process tweets
        for tweet in tweets:
            tweet_data = tweet._json
            if tweet_data:
                results.append(tweet_data)
                
            # Respect rate limits
            time.sleep(config.REQUEST_DELAY)
            
    except tweepy.TweepyException as e:
        print(f"Twitter search error: {e}")
        
    return results
    
def get_trending_topics(woeid=1):
    """
    Get trending topics on Twitter.
    
    Args:
        woeid (int): Where On Earth ID (1 = worldwide)
        
    Returns:
        list: List of trending topics
    """
    api = authenticate()
    if not api:
        return []
        
    results = []
    try:
        # Get trends
        trends = api.get_place_trends(id=woeid)
        if trends and len(trends) > 0:
            results = trends[0]['trends']
            
    except tweepy.TweepyException as e:
        print(f"Twitter trends error: {e}")
        
    return results
    
def scrape_without_api(keyword=None, max_results=20):
    """
    Scrape Twitter without API (fallback method).
    
    Args:
        keyword (str): Optional keyword to search for
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of tweet data
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
        url = 'https://twitter.com/search'
        params = {
            'q': f"{keyword if keyword else ''} filter:geo",
            'src': 'typed_query',
            'f': 'live'
        }
        
        # Make request
        response = session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find tweets (note: this is very basic and may break if Twitter changes layout)
            tweets = soup.find_all('article', {'data-testid': 'tweet'})
            
            for tweet in tweets[:max_results]:
                # Basic extraction of tweet data
                tweet_data = {}
                
                # Get user info
                user_element = tweet.find('div', {'data-testid': 'User-Name'})
                if user_element:
                    user_link = user_element.find('a')
                    if user_link:
                        username = user_link.get('href', '').strip('/')
                        tweet_data['user'] = {'screen_name': username}
                
                # Get tweet text
                text_element = tweet.find('div', {'data-testid': 'tweetText'})
                if text_element:
                    tweet_data['text'] = text_element.get_text()
                
                # Try to get location (difficult without API)
                location_element = tweet.find('span', {'data-testid': 'location'})
                if location_element:
                    location_text = location_element.get_text()
                    tweet_data['location'] = location_text
                
                # Append to results if we have at least basic info
                if 'text' in tweet_data and 'user' in tweet_data:
                    results.append(tweet_data)
                    
                # Respect rate limits
                time.sleep(config.REQUEST_DELAY)
    
    except Exception as e:
        print(f"Twitter scraping error: {e}")
    
    return results

def get_user_location(username):
    """
    Get a Twitter user's location from their profile.
    
    Args:
        username (str): Twitter username without @
        
    Returns:
        str: Location from user profile
    """
    api = authenticate()
    if not api:
        return None
        
    try:
        user = api.get_user(screen_name=username)
        return user.location
    except tweepy.TweepyException as e:
        print(f"Twitter user error: {e}")
        return None 