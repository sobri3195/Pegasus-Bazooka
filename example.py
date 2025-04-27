#!/usr/bin/env python3
"""
Example script for Pegasus-Bazooka OSINT tool.
"""

import os
import sys
from utils import mapping, data_processing
from scrapers import twitter, flickr, wikipedia

def run_example():
    """Run an example search and visualization."""
    print("Running Pegasus-Bazooka example search...")
    
    # Example coordinates (Eiffel Tower, Paris)
    latitude = 48.858370
    longitude = 2.294481
    radius_km = 5
    max_results = 30
    since_days = 30
    
    print(f"Searching for data around coordinates: {latitude}, {longitude}")
    print(f"Radius: {radius_km}km, Max results: {max_results}")
    
    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
    
    combined_results = []
    
    # Search Wikipedia
    print("Searching Wikipedia for nearby articles...")
    try:
        wiki_data = wikipedia.get_nearby_articles(
            latitude, longitude, 
            radius_km=radius_km,
            limit=max_results
        )
        
        if wiki_data:
            print(f"Found {len(wiki_data)} Wikipedia articles")
            for item in wiki_data:
                item['source'] = 'wikipedia'
                combined_results.append(item)
        else:
            print("No Wikipedia data found")
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
    
    # Normalize and merge results
    print(f"Total results: {len(combined_results)}")
    
    # Create map
    print("Creating map visualization...")
    m = mapping.create_base_map(center=[latitude, longitude])
    m = mapping.add_markers_to_map(m, combined_results, cluster=True)
    
    # Save map and data
    map_path = mapping.save_map(m, "example_map.html")
    json_path = data_processing.export_to_json(combined_results, "example_data.json")
    
    print(f"Example map saved to: {map_path}")
    print(f"Example data saved to: {json_path}")
    print("\nTo view the map, open the HTML file in your browser.")
    print("\nTo run more advanced searches, use the main.py script or launch the GUI:")
    print("  python main.py gui")
    print("  python main.py coordinates --lat 48.858370 --lon 2.294481 --radius 5 --wikipedia")
    print("  python main.py keyword --query 'Eiffel Tower' --twitter --flickr --output json")

if __name__ == "__main__":
    run_example() 