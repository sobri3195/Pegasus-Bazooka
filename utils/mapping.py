"""
Mapping utilities for Pegasus-Bazooka OSINT tool.
"""

import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
import os
from datetime import datetime
import sys
import config

def create_base_map(center=None, zoom_start=None):
    """
    Create a base map for visualization.
    
    Args:
        center (list): Center coordinates [lat, lon]
        zoom_start (int): Initial zoom level
        
    Returns:
        folium.Map: Base map object
    """
    if center is None:
        center = config.MAP_DEFAULT_LOCATION
    if zoom_start is None:
        zoom_start = config.MAP_DEFAULT_ZOOM
        
    base_map = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Add alternative tile layers
    folium.TileLayer('Stamen Terrain').add_to(base_map)
    folium.TileLayer('CartoDB positron').add_to(base_map)
    folium.TileLayer('CartoDB dark_matter').add_to(base_map)
    
    # Add layer control
    folium.LayerControl().add_to(base_map)
    
    return base_map

def add_markers_to_map(base_map, data, cluster=True):
    """
    Add markers to the map from geo data.
    
    Args:
        base_map (folium.Map): Base map object
        data (list): List of geo data points with lat, lon, and other attributes
        cluster (bool): Whether to cluster markers
        
    Returns:
        folium.Map: Updated map with markers
    """
    if not data:
        return base_map
    
    # Create a marker cluster if clustering is enabled
    if cluster:
        marker_cluster = MarkerCluster().add_to(base_map)
    
    # Add markers for each data point
    for point in data:
        if 'latitude' not in point or 'longitude' not in point:
            continue
            
        lat = point['latitude']
        lon = point['longitude']
        
        # Skip invalid coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            continue
            
        # Create popup content
        popup_html = f"<b>Source:</b> {point.get('source', 'Unknown')}<br>"
        
        if 'title' in point:
            popup_html += f"<b>Title:</b> {point['title']}<br>"
        
        if 'content' in point and point['content']:
            content = point['content']
            if len(content) > 200:
                content = content[:200] + '...'
            popup_html += f"<b>Content:</b> {content}<br>"
            
        if 'date' in point:
            popup_html += f"<b>Date:</b> {point['date']}<br>"
            
        if 'url' in point:
            popup_html += f"<b><a href='{point['url']}' target='_blank'>Open Original</a></b><br>"
        
        # Add image if available
        if 'image_url' in point and point['image_url']:
            popup_html += f"<img src='{point['image_url']}' width='200px'><br>"
        
        # Create marker with popup
        marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=point.get('title', f"{point.get('source', 'Unknown')} Data"),
            icon=get_icon_for_source(point.get('source', 'unknown'))
        )
        
        # Add to cluster or directly to map
        if cluster:
            marker.add_to(marker_cluster)
        else:
            marker.add_to(base_map)
    
    return base_map

def add_heatmap(base_map, data):
    """
    Add heatmap layer to the map.
    
    Args:
        base_map (folium.Map): Base map object
        data (list): List of geo data points with lat, lon
        
    Returns:
        folium.Map: Updated map with heatmap
    """
    if not data:
        return base_map
    
    # Extract coordinates for heatmap
    heat_data = []
    for point in data:
        if 'latitude' in point and 'longitude' in point:
            lat = point['latitude']
            lon = point['longitude']
            
            # Skip invalid coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                continue
                
            # Add weight if available
            if 'weight' in point:
                heat_data.append([lat, lon, point['weight']])
            else:
                heat_data.append([lat, lon, 1.0])
    
    # Add heatmap layer if data is available
    if heat_data:
        HeatMap(heat_data, radius=15, blur=10, gradient={
            0.4: 'blue', 0.65: 'lime', 1: 'red'
        }).add_to(base_map)
    
    return base_map

def get_icon_for_source(source):
    """
    Get appropriate icon for data source.
    
    Args:
        source (str): Source name
        
    Returns:
        folium.Icon: Icon object
    """
    source_icons = {
        'twitter': folium.Icon(color='blue', icon='twitter', prefix='fa'),
        'youtube': folium.Icon(color='red', icon='video', prefix='fa'),
        'flickr': folium.Icon(color='pink', icon='camera', prefix='fa'),
        'vk': folium.Icon(color='darkblue', icon='comments', prefix='fa'),
        'instagram': folium.Icon(color='purple', icon='instagram', prefix='fa'),
        'trendsmap': folium.Icon(color='green', icon='chart-line', prefix='fa'),
        'pastvu': folium.Icon(color='orange', icon='history', prefix='fa'),
        'wikipedia': folium.Icon(color='gray', icon='book', prefix='fa'),
        'painted_planet': folium.Icon(color='darkpurple', icon='palette', prefix='fa')
    }
    
    return source_icons.get(source.lower(), folium.Icon(color='cadetblue', icon='info-sign'))

def save_map(base_map, filename=None):
    """
    Save map to HTML file.
    
    Args:
        base_map (folium.Map): Map to save
        filename (str): Output filename
        
    Returns:
        str: Path to saved map file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pegasus_map_{timestamp}.html"
    
    output_dir = config.DEFAULT_OUTPUT_DIRECTORY
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, filename)
    base_map.save(output_path)
    return output_path 