Weather, Earthquakes & Wildfires Dashboard 🌍🚨

A real-time, multi-language (EN/GR) desktop dashboard that tracks weather conditions, active wildfires, and recent global/regional seismic activity. Built with Python and modern GUI libraries, this tool aggregates data from multiple official space and geological agencies into a single utility.

Features
- Automated Geolocation: Instantly detects the user's location via IP-API upon startup.
- Dynamic Weather Monitoring: Fetches current temperature, "feels like" temperature, humidity, wind speed, and rain probability using the Open-Meteo API.
- Global & Regional Earthquakes: Displays the 30 most recent earthquakes worldwide (or strictly within Greece when switched to Greek mode) directly from the USGS API.
- Custom Interactive Map Integration: Generates a local, dynamic map using `folium` that plots the exact coordinates and magnitudes of active earthquakes alongside the user's location.
- NASA Wildfire Tracking: Parses near-real-time satellite thermal hotspot data from NASA's FIRMS (VIIRS SNPP).
- Smart UI Controls: The "Fire Map" button remains disabled for safety and dynamically unlocks (turning red) only when active wildfires are detected within the region, launching a targeted Windy radar view.

Tech Stack & APIs
- GUI Framework: `customtkinter` (Modern Dark-mode UI)
- Mapping: `folium` (Local HTML map rendering)
- Data Fetching: `requests` (REST API management)
- APIs Integrated:
  - Open-Meteo API (Weather forecasting)
  - USGS Earthquake API (Seismic data)
  - NASA FIRMS API (Active fire hotspots)
  - IP-API (Automated user location)

Installation & Setup

1. Clone the repository:
   git clone [https://github.com/YOUR_USERNAME/weather-earthquakes-wildfires.git](https://github.com/YOUR_USERNAME/weather-earthquakes-wildfires.git)
   cd weather-earthquakes-wildfires

pip install customtkinter requests folium

python weather_earthquakes_wildfires.py
