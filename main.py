#!/usr/bin/env python3
"""
Pegasus-Bazooka OSINT Tool - Main CLI Application
"""

import argparse
import sys
import os
import json
from datetime import datetime, timedelta

from utils import mapping, data_processing
from scrapers import twitter, flickr, wikipedia

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Pegasus-Bazooka OSINT Tool for geolocation data collection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create subparsers for different search modes
    subparsers = parser.add_subparsers(dest="mode", help="Search mode")
    
    # Coordinates-based search
    coord_parser = subparsers.add_parser("coordinates", help="Search by coordinates")
    coord_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    coord_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    coord_parser.add_argument("--radius", type=float, default=10, help="Search radius in kilometers")
    
    # Keyword-based search
    keyword_parser = subparsers.add_parser("keyword", help="Search by keyword")
    keyword_parser.add_argument("--query", type=str, required=True, help="Keyword or phrase to search for")
    
    # Date filter (for both modes)
    for subp in [coord_parser, keyword_parser]:
        date_group = subp.add_argument_group("Date filters")
        date_group.add_argument("--days", type=int, default=7, help="Get data from the last X days")
        date_group.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
        date_group.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    
    # Data sources (for both modes)
    for subp in [coord_parser, keyword_parser]:
        source_group = subp.add_argument_group("Data sources")
        source_group.add_argument("--twitter", action="store_true", help="Collect data from Twitter")
        source_group.add_argument("--flickr", action="store_true", help="Collect data from Flickr")
        source_group.add_argument("--youtube", action="store_true", help="Collect data from YouTube")
        source_group.add_argument("--wikipedia", action="store_true", help="Collect data from Wikipedia")
        source_group.add_argument("--vk", action="store_true", help="Collect data from VK.com")
        source_group.add_argument("--instagram", action="store_true", help="Collect data from Instagram")
        source_group.add_argument("--trendsmap", action="store_true", help="Collect data from Trendsmap")
        source_group.add_argument("--pastvu", action="store_true", help="Collect data from Pastvu")
        source_group.add_argument("--painted-planet", action="store_true", help="Collect data from Painted Planet")
        source_group.add_argument("--all", action="store_true", help="Collect data from all available sources")
    
    # Output options (for both modes)
    for subp in [coord_parser, keyword_parser]:
        output_group = subp.add_argument_group("Output options")
        output_group.add_argument("--output", type=str, choices=["json", "csv", "map", "all"], default="all",
                               help="Output format")
        output_group.add_argument("--output-file", type=str, help="Output file name")
        output_group.add_argument("--max-results", type=int, default=100, 
                               help="Maximum number of results per source")
        output_group.add_argument("--cluster", action="store_true", default=True,
                               help="Cluster markers on map")
        output_group.add_argument("--heatmap", action="store_true", help="Add heatmap layer to map")
    
    # Add GUI mode
    gui_parser = subparsers.add_parser("gui", help="Launch the graphical user interface")
    
    return parser.parse_args()

def process_date_args(args):
    """Process date arguments and return start/end dates."""
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid start date format. Use YYYY-MM-DD.")
            sys.exit(1)
    elif args.days:
        start_date = datetime.now() - timedelta(days=args.days)
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid end date format. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        end_date = datetime.now()
    
    return start_date, end_date

def collect_data(args):
    """Collect data from selected sources based on arguments."""
    # Process date arguments
    start_date, end_date = process_date_args(args)
    
    # Determine which sources to use
    sources = []
    if args.all:
        sources = ["twitter", "flickr", "youtube", "wikipedia", "vk", "instagram", 
                  "trendsmap", "pastvu", "painted_planet"]
    else:
        if args.twitter:
            sources.append("twitter")
        if args.flickr:
            sources.append("flickr")
        if args.youtube:
            sources.append("youtube")
        if args.wikipedia:
            sources.append("wikipedia")
        if args.vk:
            sources.append("vk")
        if args.instagram:
            sources.append("instagram")
        if args.trendsmap:
            sources.append("trendsmap")
        if args.pastvu:
            sources.append("pastvu")
        if args.painted_planet:
            sources.append("painted_planet")
    
    # If no sources specified, use default sources
    if not sources:
        sources = ["twitter", "flickr", "wikipedia"]
    
    # Collect data from each source
    results = {}
    combined_results = []
    
    print(f"[*] Starting data collection from {len(sources)} sources...")
    
    for source in sources:
        print(f"[*] Collecting data from {source.capitalize()}...")
        
        if source == "twitter":
            if args.mode == "coordinates":
                raw_data = twitter.search_by_location(
                    args.lat, args.lon, args.radius, 
                    max_results=args.max_results,
                    since_days=(datetime.now() - start_date).days
                )
            else:  # keyword mode
                raw_data = twitter.search_by_keyword(
                    args.query,
                    max_results=args.max_results,
                    since_days=(datetime.now() - start_date).days
                )
                
            # Normalize data
            normalized_data = []
            for item in raw_data:
                normalized = data_processing.normalize_data(item, 'twitter')
                if normalized['latitude'] is not None and normalized['longitude'] is not None:
                    normalized_data.append(normalized)
                    
            results[source] = normalized_data
            combined_results.extend(normalized_data)
            
        elif source == "flickr":
            if args.mode == "coordinates":
                raw_data = flickr.search_by_location(
                    args.lat, args.lon, args.radius, 
                    max_results=args.max_results,
                    since_days=(datetime.now() - start_date).days
                )
            else:  # keyword mode
                raw_data = flickr.search_by_keyword(
                    args.query,
                    max_results=args.max_results,
                    since_days=(datetime.now() - start_date).days
                )
                
            # Normalize data
            normalized_data = []
            for item in raw_data:
                normalized = data_processing.normalize_data(item, 'flickr')
                if normalized['latitude'] is not None and normalized['longitude'] is not None:
                    normalized_data.append(normalized)
                    
            results[source] = normalized_data
            combined_results.extend(normalized_data)
            
        elif source == "wikipedia":
            if args.mode == "coordinates":
                raw_data = wikipedia.get_nearby_articles(
                    args.lat, args.lon, 
                    radius_km=args.radius,
                    limit=args.max_results
                )
            else:  # keyword mode
                raw_data = wikipedia.search_articles(
                    args.query,
                    limit=args.max_results
                )
                
            # Process results (already in normalized format from the API)
            wiki_data = []
            for item in raw_data:
                item['source'] = 'wikipedia'
                wiki_data.append(item)
                    
            results[source] = wiki_data
            combined_results.extend(wiki_data)
            
        # Add other sources as they're implemented
    
    print(f"[+] Data collection completed. Found {len(combined_results)} results.")
    
    # Apply filters
    if start_date or end_date:
        print(f"[*] Filtering by date: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        combined_results = data_processing.filter_by_date(combined_results, start_date, end_date)
        
    if args.mode == "keyword" and args.query:
        print(f"[*] Filtering by keyword: {args.query}")
        combined_results = data_processing.filter_by_keyword(combined_results, [args.query])
    
    print(f"[+] After filtering: {len(combined_results)} results.")
    
    return results, combined_results

def output_results(args, combined_results):
    """Output results based on specified format."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.output_file:
        base_filename = args.output_file
        # Remove extension if present
        if "." in base_filename:
            base_filename = base_filename.split(".")[0]
    else:
        base_filename = f"pegasus_data_{timestamp}"
    
    # Output to map
    if args.output in ["map", "all"]:
        print(f"[*] Generating map...")
        
        # Create map
        if args.mode == "coordinates":
            center = [args.lat, args.lon]
        elif combined_results and len(combined_results) > 0:
            center = [combined_results[0].get('latitude', 0), combined_results[0].get('longitude', 0)]
        else:
            center = None
            
        m = mapping.create_base_map(center=center)
        
        # Add markers
        m = mapping.add_markers_to_map(m, combined_results, cluster=args.cluster)
        
        # Add heatmap if enabled
        if args.heatmap:
            m = mapping.add_heatmap(m, combined_results)
        
        # Save map
        map_file = f"{base_filename}.html"
        map_path = mapping.save_map(m, map_file)
        print(f"[+] Map saved to: {map_path}")
    
    # Output to CSV
    if args.output in ["csv", "all"]:
        print(f"[*] Exporting to CSV...")
        csv_file = f"{base_filename}.csv"
        csv_path = data_processing.export_to_csv(combined_results, csv_file)
        print(f"[+] CSV data saved to: {csv_path}")
    
    # Output to JSON
    if args.output in ["json", "all"]:
        print(f"[*] Exporting to JSON...")
        json_file = f"{base_filename}.json"
        json_path = data_processing.export_to_json(combined_results, json_file)
        print(f"[+] JSON data saved to: {json_path}")

def launch_gui():
    """Launch the Streamlit GUI."""
    try:
        import streamlit
        import subprocess
        import os
        
        # Get the path to the streamlit app
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui", "streamlit_app.py")
        
        print(f"[*] Launching GUI... Please wait a moment.")
        subprocess.run(["streamlit", "run", script_path])
        
    except ImportError:
        print("[!] Error: Streamlit is not installed. Install with 'pip install streamlit'.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error launching GUI: {e}")
        sys.exit(1)

def main():
    """Main function."""
    print("""
    ██████╗ ███████╗ ██████╗  █████╗ ███████╗██╗   ██╗███████╗      
    ██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝██║   ██║██╔════╝      
    ██████╔╝█████╗  ██║  ███╗███████║███████╗██║   ██║███████╗      
    ██╔═══╝ ██╔══╝  ██║   ██║██╔══██║╚════██║██║   ██║╚════██║      
    ██║     ███████╗╚██████╔╝██║  ██║███████║╚██████╔╝███████║      
    ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝      
                                                                     
    ██████╗  █████╗ ███████╗ ██████╗  ██████╗ ██╗  ██╗ █████╗       
    ██╔══██╗██╔══██╗╚══███╔╝██╔═══██╗██╔═══██╗██║ ██╔╝██╔══██╗      
    ██████╔╝███████║  ███╔╝ ██║   ██║██║   ██║█████╔╝ ███████║      
    ██╔══██╗██╔══██║ ███╔╝  ██║   ██║██║   ██║██╔═██╗ ██╔══██║      
    ██████╔╝██║  ██║███████╗╚██████╔╝╚██████╔╝██║  ██╗██║  ██║      
    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝      
    
    OSINT Tool for geolocation data collection
    Author: Letda Kes dr. Sobri, S.Kom
    GitHub: github.com/sobri3195
    
    """)
    
    args = parse_arguments()
    
    # Handle GUI mode
    if args.mode == "gui":
        launch_gui()
        return
    
    # Handle other modes
    if args.mode in ["coordinates", "keyword"]:
        results, combined_results = collect_data(args)
        output_results(args, combined_results)
    else:
        print("[!] Error: No mode specified. Use 'coordinates', 'keyword', or 'gui'.")
        sys.exit(1)

if __name__ == "__main__":
    main() 