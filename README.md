# Pegasus-Bazooka

A powerful OSINT (Open Source Intelligence) tool for gathering geolocation data from various social media and open data sources.

## Overview

Pegasus-Bazooka is designed to automatically collect and visualize location-based information from multiple platforms including Twitter, YouTube, Flickr, VK.com, Instagram, and other sources. The tool provides an interactive map interface to display results and supports various search criteria.

## Features

- **Multi-platform Data Collection**:
  - Twitter geolocation posts
  - YouTube GeoFind (location-based videos)
  - Flickr geotagged photos
  - VK.com geotagged photos
  - Instagram location-based posts via Huntel.io
  - Twitter trends from Trendsmap
  - Historical photos from Pastvu.com
  - Nearby Wikipedia articles
  - Art locations from Painted Planet

- **Search Options**:
  - By coordinates and radius
  - By keywords
  - By date/time range

- **Output Formats**:
  - Interactive map visualization
  - CSV export
  - JSON export

## Installation

```bash
# Clone the repository
git clone https://github.com/sobri3195/pegasus-bazooka.git
cd pegasus-bazooka

# Install requirements
pip install -r requirements.txt
```

## Usage

```bash
# Run the command line interface
python main.py --help

# Run the web interface (if streamlit is installed)
streamlit run gui/streamlit_app.py
```

## Project Structure

- `scrapers/`: Modules for scraping different platforms
- `utils/`: Helper functions for mapping, data processing, and export
- `gui/`: Streamlit web interface

## Requirements

- Python 3.7+
- See requirements.txt for dependencies

## Author

**Letda Kes dr. Sobri, S.Kom**

- GitHub: [github.com/sobri3195](https://github.com/sobri3195)
- Email: muhammadsobrimaulana31@gmail.com
- Donation: [https://lynk.id/muhsobrimaulana](https://lynk.id/muhsobrimaulana)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
