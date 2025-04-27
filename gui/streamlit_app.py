"""
Streamlit web interface for Pegasus-Bazooka OSINT tool.
"""

import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import sys
import os
import json
import datetime
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils import mapping, data_processing
from scrapers import twitter, flickr, wikipedia

# Set page configuration
st.set_page_config(
    page_title="Pegasus-Bazooka OSINT Tool",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066cc;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4d4d4d;
    }
    .info-text {
        font-size: 1rem;
        color: #4d4d4d;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .footer {
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #e6e6e6;
        text-align: center;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🦅 Pegasus-Bazooka</p>', unsafe_allow_html=True)
st.markdown('<p class="info-text">OSINT Tool for geolocation data gathering</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<p class="sub-header">Search Options</p>', unsafe_allow_html=True)

# Search by coordinates
st.sidebar.markdown("### Search by Coordinates")
latitude = st.sidebar.number_input("Latitude", value=0.0, min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f")
longitude = st.sidebar.number_input("Longitude", value=0.0, min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f")
radius = st.sidebar.slider("Radius (km)", min_value=1, max_value=50, value=10)

# Search by keyword
st.sidebar.markdown("### Search by Keyword")
keyword = st.sidebar.text_input("Keyword")

# Date range
st.sidebar.markdown("### Date Range")
date_option = st.sidebar.radio("Date Option", ["Last 7 days", "Last 30 days", "Custom range"])

if date_option == "Custom range":
    start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=7))
    end_date = st.sidebar.date_input("End Date", datetime.now())
else:
    if date_option == "Last 7 days":
        days = 7
    else:  # Last 30 days
        days = 30
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

# Data sources
st.sidebar.markdown("### Data Sources")
twitter_enabled = st.sidebar.checkbox("Twitter", value=True)
flickr_enabled = st.sidebar.checkbox("Flickr", value=True)
youtube_enabled = st.sidebar.checkbox("YouTube", value=False)
wikipedia_enabled = st.sidebar.checkbox("Wikipedia", value=True)
vk_enabled = st.sidebar.checkbox("VK.com", value=False)
instagram_enabled = st.sidebar.checkbox("Instagram", value=False)
trendsmap_enabled = st.sidebar.checkbox("Trendsmap", value=False)
pastvu_enabled = st.sidebar.checkbox("Pastvu", value=False)
painted_planet_enabled = st.sidebar.checkbox("Painted Planet", value=False)

# Results limit
st.sidebar.markdown("### Results Limit")
max_results = st.sidebar.slider("Max Results per Source", min_value=10, max_value=200, value=50)

# Output options
st.sidebar.markdown("### Output Options")
output_format = st.sidebar.selectbox("Output Format", ["JSON", "CSV"])
cluster_markers = st.sidebar.checkbox("Cluster Markers", value=True)
show_heatmap = st.sidebar.checkbox("Show Heatmap", value=False)

# Main content area - tabs
tab1, tab2, tab3 = st.tabs(["Map", "Data Table", "Raw Data"])

# Generate a unique session ID for file naming
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Search button
if st.sidebar.button("Search"):
    # Show progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # Initialize result container
    if 'results' not in st.session_state:
        st.session_state.results = {}
    
    # Initialize combined results
    combined_results = []
    
    # Search in Twitter
    if twitter_enabled:
        progress_text.text("Searching Twitter...")
        
        twitter_results = []
        try:
            if latitude != 0 and longitude != 0:
                # Search by location
                raw_results = twitter.search_by_location(
                    latitude,
                    longitude,
                    radius,
                    max_results=max_results,
                    since_days=(datetime.now() - start_date).days
                )
            elif keyword:
                # Search by keyword
                raw_results = twitter.search_by_keyword(
                    keyword,
                    max_results=max_results,
                    since_days=(datetime.now() - start_date).days
                )
            else:
                raw_results = []
                
            # Normalize data
            for item in raw_results:
                normalized = data_processing.normalize_data(item, 'twitter')
                if normalized['latitude'] is not None and normalized['longitude'] is not None:
                    twitter_results.append(normalized)
                    
        except Exception as e:
            st.error(f"Twitter search error: {e}")
            
        # Update progress
        progress_bar.progress(20)
        
        # Store results
        st.session_state.results['twitter'] = twitter_results
        combined_results.extend(twitter_results)
    
    # Search in Flickr
    if flickr_enabled:
        progress_text.text("Searching Flickr...")
        
        flickr_results = []
        try:
            if latitude != 0 and longitude != 0:
                # Search by location
                raw_results = flickr.search_by_location(
                    latitude,
                    longitude,
                    radius,
                    max_results=max_results,
                    since_days=(datetime.now() - start_date).days
                )
            elif keyword:
                # Search by keyword
                raw_results = flickr.search_by_keyword(
                    keyword,
                    max_results=max_results,
                    since_days=(datetime.now() - start_date).days
                )
            else:
                raw_results = []
                
            # Normalize data
            for item in raw_results:
                normalized = data_processing.normalize_data(item, 'flickr')
                if normalized['latitude'] is not None and normalized['longitude'] is not None:
                    flickr_results.append(normalized)
                    
        except Exception as e:
            st.error(f"Flickr search error: {e}")
            
        # Update progress
        progress_bar.progress(40)
        
        # Store results
        st.session_state.results['flickr'] = flickr_results
        combined_results.extend(flickr_results)
    
    # Search in Wikipedia
    if wikipedia_enabled:
        progress_text.text("Searching Wikipedia...")
        
        wiki_results = []
        try:
            if latitude != 0 and longitude != 0:
                # Get nearby articles
                raw_results = wikipedia.get_nearby_articles(
                    latitude,
                    longitude,
                    radius_km=radius,
                    limit=max_results
                )
            elif keyword:
                # Search by keyword
                raw_results = wikipedia.search_articles(
                    keyword,
                    limit=max_results
                )
            else:
                raw_results = []
                
            # Process results (already in normalized format from the API)
            for item in raw_results:
                item['source'] = 'wikipedia'
                wiki_results.append(item)
                    
        except Exception as e:
            st.error(f"Wikipedia search error: {e}")
            
        # Update progress
        progress_bar.progress(60)
        
        # Store results
        st.session_state.results['wikipedia'] = wiki_results
        combined_results.extend(wiki_results)
    
    # Update progress
    progress_bar.progress(80)
    progress_text.text("Processing results...")
    
    # Filter results by date if specified
    if start_date and end_date:
        combined_results = data_processing.filter_by_date(
            combined_results,
            start_date=start_date,
            end_date=end_date
        )
    
    # Filter results by keyword if specified and not already filtered
    if keyword and (latitude != 0 and longitude != 0):
        combined_results = data_processing.filter_by_keyword(
            combined_results,
            [keyword]
        )
    
    # Store combined results
    st.session_state.combined_results = combined_results
    
    # Export results
    if output_format == "JSON":
        output_file = f"pegasus_data_{st.session_state.session_id}.json"
        data_processing.export_to_json(combined_results, output_file)
    else:  # CSV
        output_file = f"pegasus_data_{st.session_state.session_id}.csv"
        data_processing.export_to_csv(combined_results, output_file)
    
    # Update progress
    progress_bar.progress(100)
    progress_text.text(f"Search completed! Found {len(combined_results)} results.")
    
    # Hide progress after 2 seconds
    import time
    time.sleep(2)
    progress_bar.empty()
    progress_text.empty()

# Display results
if 'combined_results' in st.session_state and st.session_state.combined_results:
    results = st.session_state.combined_results
    
    # Create map in the Map tab
    with tab1:
        st.markdown('<p class="sub-header">Interactive Map</p>', unsafe_allow_html=True)
        
        # Create base map
        if latitude != 0 and longitude != 0:
            center = [latitude, longitude]
        elif results and len(results) > 0 and 'latitude' in results[0] and 'longitude' in results[0]:
            center = [results[0]['latitude'], results[0]['longitude']]
        else:
            center = None
            
        m = mapping.create_base_map(center=center)
        
        # Add markers
        m = mapping.add_markers_to_map(m, results, cluster=cluster_markers)
        
        # Add heatmap if enabled
        if show_heatmap:
            m = mapping.add_heatmap(m, results)
        
        # Display map
        folium_static(m, width=1000, height=600)
        
        # Map summary
        source_counts = {}
        for item in results:
            source = item.get('source', 'unknown')
            if source in source_counts:
                source_counts[source] += 1
            else:
                source_counts[source] = 1
                
        st.markdown('<p class="highlight info-text">Results by source:</p>', unsafe_allow_html=True)
        for source, count in source_counts.items():
            st.markdown(f"* **{source.capitalize()}**: {count} results")
    
    # Create data table in the Data Table tab
    with tab2:
        st.markdown('<p class="sub-header">Data Table</p>', unsafe_allow_html=True)
        
        # Convert to DataFrame for display
        df = pd.DataFrame(results)
        
        # Drop raw_data column if exists
        if 'raw_data' in df.columns:
            df = df.drop('raw_data', axis=1)
            
        # Rearrange columns
        important_cols = ['source', 'title', 'content', 'date', 'latitude', 'longitude', 'url']
        other_cols = [col for col in df.columns if col not in important_cols]
        final_cols = important_cols + other_cols
        
        # Select only columns that exist in the DataFrame
        existing_cols = [col for col in final_cols if col in df.columns]
        df = df[existing_cols]
        
        # Display table
        st.dataframe(df, height=600)
        
        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"pegasus_data_{st.session_state.session_id}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Prepare data for JSON export
            json_data = []
            for _, row in df.iterrows():
                json_data.append(row.to_dict())
                
            st.download_button(
                label="Download as JSON",
                data=json.dumps(json_data, ensure_ascii=False, indent=2),
                file_name=f"pegasus_data_{st.session_state.session_id}.json",
                mime="application/json"
            )
    
    # Display raw data in the Raw Data tab
    with tab3:
        st.markdown('<p class="sub-header">Raw Data</p>', unsafe_allow_html=True)
        
        # Display source selection
        sources = list(st.session_state.results.keys())
        selected_source = st.selectbox("Select Source", sources)
        
        if selected_source in st.session_state.results:
            source_data = st.session_state.results[selected_source]
            
            if source_data:
                # Display sample of raw data
                st.json(source_data[0])
            else:
                st.info(f"No data available for {selected_source}")
        else:
            st.info("No source selected")

else:
    # Display instructions if no search has been performed
    with tab1:
        st.markdown('<p class="highlight info-text">No data to display. Please configure search options and click "Search" to begin.</p>', unsafe_allow_html=True)
        
        # Display example map
        m = mapping.create_base_map()
        folium_static(m, width=1000, height=600)

# Footer
st.markdown("""
<div class="footer">
    <p>Pegasus-Bazooka OSINT Tool | Author: Letda Kes dr. Sobri, S.Kom | <a href="https://github.com/sobri3195">GitHub</a> | <a href="mailto:muhammadsobrimaulana31@gmail.com">Contact</a> | <a href="https://lynk.id/muhsobrimaulana">Donate</a></p>
</div>
""", unsafe_allow_html=True) 