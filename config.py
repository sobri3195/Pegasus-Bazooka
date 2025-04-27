"""
Configuration settings for Pegasus-Bazooka OSINT tool.
"""

# API Keys - Replace with your actual API keys
API_KEYS = {
    'twitter': {
        'api_key': 'YOUR_TWITTER_API_KEY',
        'api_secret': 'YOUR_TWITTER_API_SECRET',
        'access_token': 'YOUR_TWITTER_ACCESS_TOKEN',
        'access_token_secret': 'YOUR_TWITTER_ACCESS_TOKEN_SECRET'
    },
    'flickr': {
        'api_key': 'YOUR_FLICKR_API_KEY',
        'api_secret': 'YOUR_FLICKR_API_SECRET'
    },
    'google': {
        'api_key': 'YOUR_GOOGLE_API_KEY'  # For YouTube and Maps
    },
    'wikipedia': {
        'user_agent': 'Pegasus-Bazooka/1.0 (muhammadsobrimaulana31@gmail.com)'
    }
}

# Default search parameters
DEFAULT_SEARCH_RADIUS = 10  # km
DEFAULT_RESULTS_LIMIT = 100
DEFAULT_TIME_RANGE = 7  # days

# Map settings
MAP_DEFAULT_ZOOM = 10
MAP_DEFAULT_LOCATION = [0, 0]  # Default center of the map [lat, lon]

# Output settings
DEFAULT_OUTPUT_FORMAT = 'json'  # 'json' or 'csv'
DEFAULT_OUTPUT_DIRECTORY = 'results'

# User-agent for web scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Request settings
REQUEST_TIMEOUT = 30  # seconds
REQUEST_RETRIES = 3
REQUEST_DELAY = 1  # seconds between requests

# Enable/Disable specific data sources
ENABLED_SOURCES = {
    'twitter': True,
    'youtube': True,
    'flickr': True,
    'vk': True,
    'instagram': True,
    'trendsmap': True,
    'pastvu': True,
    'wikipedia': True,
    'painted_planet': True
} 