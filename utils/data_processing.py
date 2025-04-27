"""
Data processing utilities for Pegasus-Bazooka OSINT tool.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import os
import config
from geopy.distance import geodesic

def normalize_data(data, source):
    """
    Normalize data from different sources to a common format.
    
    Args:
        data (dict): Raw data from a source
        source (str): Name of the source
        
    Returns:
        dict: Normalized data
    """
    normalized = {
        'source': source,
        'latitude': None,
        'longitude': None,
        'title': '',
        'content': '',
        'date': None,
        'url': '',
        'image_url': '',
        'raw_data': data
    }
    
    # Extract fields based on source
    if source == 'twitter':
        if 'geo' in data and data['geo'] and 'coordinates' in data['geo']:
            normalized['latitude'] = data['geo']['coordinates'][0]
            normalized['longitude'] = data['geo']['coordinates'][1]
        elif 'place' in data and data['place'] and 'bounding_box' in data['place']:
            # Calculate center of bounding box
            coords = data['place']['bounding_box']['coordinates'][0]
            lat_sum = sum(c[1] for c in coords)
            lon_sum = sum(c[0] for c in coords)
            normalized['latitude'] = lat_sum / len(coords)
            normalized['longitude'] = lon_sum / len(coords)
            
        normalized['title'] = f"@{data.get('user', {}).get('screen_name', '')}"
        normalized['content'] = data.get('text', '')
        
        if 'created_at' in data:
            normalized['date'] = data['created_at']
            
        if 'id_str' in data and 'user' in data and 'screen_name' in data['user']:
            normalized['url'] = f"https://twitter.com/{data['user']['screen_name']}/status/{data['id_str']}"
            
        if 'entities' in data and 'media' in data['entities'] and data['entities']['media']:
            normalized['image_url'] = data['entities']['media'][0].get('media_url_https', '')
    
    elif source == 'youtube':
        if 'location' in data and 'latitude' in data['location'] and 'longitude' in data['location']:
            normalized['latitude'] = data['location']['latitude']
            normalized['longitude'] = data['location']['longitude']
            
        normalized['title'] = data.get('title', '')
        normalized['content'] = data.get('description', '')
        
        if 'published_at' in data:
            normalized['date'] = data['published_at']
            
        if 'id' in data:
            normalized['url'] = f"https://www.youtube.com/watch?v={data['id']}"
            
        if 'thumbnail_url' in data:
            normalized['image_url'] = data['thumbnail_url']
    
    elif source == 'flickr':
        if 'latitude' in data and 'longitude' in data:
            normalized['latitude'] = float(data['latitude'])
            normalized['longitude'] = float(data['longitude'])
            
        normalized['title'] = data.get('title', '')
        normalized['content'] = data.get('description', '')
        
        if 'date_taken' in data:
            normalized['date'] = data['date_taken']
            
        if 'id' in data and 'owner' in data:
            normalized['url'] = f"https://www.flickr.com/photos/{data['owner']}/{data['id']}"
            
        if 'url_m' in data:
            normalized['image_url'] = data['url_m']
    
    # Add more sources as needed...
    
    return normalized

def filter_by_coordinates(data, center_lat, center_lon, radius_km):
    """
    Filter data points by distance from a center point.
    
    Args:
        data (list): List of data points
        center_lat (float): Center latitude
        center_lon (float): Center longitude
        radius_km (float): Radius in kilometers
        
    Returns:
        list: Filtered data points
    """
    center = (center_lat, center_lon)
    filtered_data = []
    
    for point in data:
        if 'latitude' in point and 'longitude' in point:
            point_coords = (point['latitude'], point['longitude'])
            distance = geodesic(center, point_coords).kilometers
            
            if distance <= radius_km:
                point['distance'] = distance
                filtered_data.append(point)
    
    return filtered_data

def filter_by_date(data, start_date=None, end_date=None):
    """
    Filter data points by date range.
    
    Args:
        data (list): List of data points
        start_date (datetime): Start date
        end_date (datetime): End date
        
    Returns:
        list: Filtered data points
    """
    if not start_date and not end_date:
        return data
        
    filtered_data = []
    
    for point in data:
        if 'date' not in point or not point['date']:
            continue
            
        # Convert string date to datetime if needed
        point_date = point['date']
        if isinstance(point_date, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S%z', '%a %b %d %H:%M:%S %z %Y']:
                    try:
                        point_date = datetime.strptime(point_date, fmt)
                        break
                    except ValueError:
                        continue
            except Exception:
                continue
                
        # Skip if conversion failed
        if not isinstance(point_date, datetime):
            continue
            
        # Apply date filters
        if start_date and point_date < start_date:
            continue
        if end_date and point_date > end_date:
            continue
            
        filtered_data.append(point)
    
    return filtered_data

def filter_by_keyword(data, keywords):
    """
    Filter data points by keywords.
    
    Args:
        data (list): List of data points
        keywords (list): List of keywords to search for
        
    Returns:
        list: Filtered data points
    """
    if not keywords:
        return data
        
    # Convert keywords to lowercase for case-insensitive matching
    keywords = [k.lower() for k in keywords]
    filtered_data = []
    
    for point in data:
        # Check title and content for keywords
        title = point.get('title', '').lower()
        content = point.get('content', '').lower()
        text = title + ' ' + content
        
        if any(keyword in text for keyword in keywords):
            filtered_data.append(point)
    
    return filtered_data

def merge_data_sources(data_sources):
    """
    Merge data from multiple sources.
    
    Args:
        data_sources (dict): Dictionary of data sources and their data points
        
    Returns:
        list: Merged data
    """
    merged_data = []
    
    for source, data in data_sources.items():
        if data:
            merged_data.extend(data)
    
    return merged_data

def export_to_csv(data, filename=None):
    """
    Export data to CSV file.
    
    Args:
        data (list): List of data points
        filename (str): Output filename
        
    Returns:
        str: Path to saved CSV file
    """
    if not data:
        return None
        
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pegasus_data_{timestamp}.csv"
    
    output_dir = config.DEFAULT_OUTPUT_DIRECTORY
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, filename)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Remove raw_data column if exists (too large)
    if 'raw_data' in df.columns:
        df = df.drop('raw_data', axis=1)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    return output_path

def export_to_json(data, filename=None):
    """
    Export data to JSON file.
    
    Args:
        data (list): List of data points
        filename (str): Output filename
        
    Returns:
        str: Path to saved JSON file
    """
    if not data:
        return None
        
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pegasus_data_{timestamp}.json"
    
    output_dir = config.DEFAULT_OUTPUT_DIRECTORY
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, filename)
    
    # Prepare data for serialization
    serializable_data = []
    for item in data:
        serializable_item = item.copy()
        # Remove raw_data if exists
        if 'raw_data' in serializable_item:
            del serializable_item['raw_data']
            
        # Convert datetime objects to strings
        for key, value in serializable_item.items():
            if isinstance(value, datetime):
                serializable_item[key] = value.isoformat()
                
        serializable_data.append(serializable_item)
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, ensure_ascii=False, indent=2)
    
    return output_path 