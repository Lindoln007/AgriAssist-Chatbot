import requests
from datetime import datetime

# Dictionary of Malawi districts and major locations with their coordinates
MALAWI_LOCATIONS = {
    # Northern Region
    "chitipa": {"lat": -9.7033, "lon": 33.2700},
    "karonga": {"lat": -9.9333, "lon": 33.9333},
    "likoma": {"lat": -12.0667, "lon": 34.7333},
    "mzimba": {"lat": -11.9000, "lon": 33.6000},
    "mzuzu": {"lat": -11.4656, "lon": 34.0207},
    "nkhata bay": {"lat": -11.6066, "lon": 34.2907},
    "rumphi": {"lat": -11.0167, "lon": 33.8667},
    
    # Central Region
    "dedza": {"lat": -14.3833, "lon": 34.3333},
    "dowa": {"lat": -13.6500, "lon": 33.9333},
    "kasungu": {"lat": -13.0333, "lon": 33.4833},
    "lilongwe": {"lat": -13.9833, "lon": 33.7833},
    "mchinji": {"lat": -13.8000, "lon": 32.8833},
    "nkhotakota": {"lat": -12.9333, "lon": 34.3000},
    "ntcheu": {"lat": -14.8200, "lon": 34.6358},
    "ntchisi": {"lat": -13.3667, "lon": 33.9167},
    "salima": {"lat": -13.7804, "lon": 34.4587},
    
    # Southern Region
    "balaka": {"lat": -14.9833, "lon": 34.9500},
    "blantyre": {"lat": -15.7861, "lon": 35.0058},
    "chikwawa": {"lat": -16.0333, "lon": 34.8000},
    "chiradzulu": {"lat": -15.7000, "lon": 35.1833},
    "machinga": {"lat": -15.1667, "lon": 35.3000},
    "mangochi": {"lat": -14.4782, "lon": 35.2645},
    "mulanje": {"lat": -16.0316, "lon": 35.5000},
    "mwanza": {"lat": -15.6000, "lon": 34.5167},
    "neno": {"lat": -15.5167, "lon": 34.6667},
    "nsanje": {"lat": -16.9167, "lon": 35.2667},
    "phalombe": {"lat": -15.8064, "lon": 35.6507},
    "thyolo": {"lat": -16.0667, "lon": 35.1333},
    "zomba": {"lat": -15.3833, "lon": 35.3333}
}

def get_coordinates(location_name):
    """
    Get coordinates for a given location name in Malawi.
    Returns a dict with 'lat', 'lon', and formatted 'name' or None if not found.
    """
    if not location_name:
        return None
        
    # Normalize input
    key = location_name.lower().strip()
    
    # Direct lookup
    if key in MALAWI_LOCATIONS:
        return {
            "name": key.title(),
            "lat": MALAWI_LOCATIONS[key]["lat"],
            "lon": MALAWI_LOCATIONS[key]["lon"]
        }
    
    # Partial match lookup (e.g. "Lilongwe City" -> "lilongwe")
    for loc, coords in MALAWI_LOCATIONS.items():
        if loc in key or key in loc:
            return {
                "name": loc.title(),
                "lat": coords["lat"],
                "lon": coords["lon"]
            }
            
    return None

def get_weather_forecast(lat, lon):
    """
    Fetch weather forecast from Open-Meteo API.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,cloudcover,windspeed_10m,soil_moisture_0_1cm",
            "forecast_days": 1,
            "current_weather": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def analyze_weather_for_farming(weather_data):
    """
    Analyze weather data and provide farming recommendations.
    """
    if not weather_data or 'current_weather' not in weather_data:
        return "Weather data unavailable for analysis."
        
    current = weather_data['current_weather']
    hourly = weather_data.get('hourly', {})
    
    temp = current.get('temperature')
    wind_speed = current.get('windspeed')
    
    # Calculate daily averages/totals if available
    precip_prob = 0
    avg_humidity = 0
    avg_soil_moisture = 0
    
    if hourly:
        if 'precipitation' in hourly:
            total_precip = sum(hourly['precipitation'])
            precip_prob = 100 if total_precip > 0.5 else 0 # Simplified
        
        if 'relative_humidity_2m' in hourly:
            avg_humidity = sum(hourly['relative_humidity_2m']) / len(hourly['relative_humidity_2m'])
            
        if 'soil_moisture_0_1cm' in hourly:
            avg_soil_moisture = sum(hourly['soil_moisture_0_1cm']) / len(hourly['soil_moisture_0_1cm'])

    recommendations = []
    
    # 1. Irrigation Advice
    if precip_prob > 50:
        recommendations.append("🌧️ <strong>Irrigation:</strong> Rain is expected. Suspend irrigation to save water and prevent waterlogging.")
    elif avg_soil_moisture < 0.2:
        recommendations.append("💧 <strong>Irrigation:</strong> Soil moisture is low. Irrigation is recommended, preferably in the early morning or late afternoon.")
    else:
        recommendations.append("✅ <strong>Irrigation:</strong> Soil moisture levels are adequate. No immediate irrigation needed.")

    # 2. Planting/Harvesting
    if precip_prob > 20:
        recommendations.append("🚜 <strong>Field Work:</strong> Avoid applying fertilizers or pesticides today as rain may wash them away. Delay harvesting to prevent crop spoilage.")
    elif wind_speed > 20:
        recommendations.append("💨 <strong>Spraying:</strong> High wind speeds detected. Avoid spraying pesticides to prevent drift.")
    else:
        recommendations.append("🌱 <strong>Field Work:</strong> Conditions are favorable for planting, weeding, and applying fertilizers.")

    # 3. Pest & Disease
    if avg_humidity > 80 and temp > 20:
        recommendations.append("🐛 <strong>Pests & Disease:</strong> High humidity and warm temperatures favor fungal diseases like blight. Monitor crops closely.")
    
    # 4. Livestock
    if temp > 30:
        recommendations.append("🐄 <strong>Livestock:</strong> High temperatures expected. Ensure animals have plenty of shade and water to prevent heat stress.")
    elif temp < 15:
        recommendations.append("🐔 <strong>Livestock:</strong> Cooler temperatures expected. Ensure young animals (chicks, piglets) have adequate warmth.")

    return "\n\n".join(recommendations)

def extract_location_from_text(text):
    """
    Extract a Malawi district/location from the given text.
    Returns the location name if found, else None.
    """
    if not text:
        return None
        
    text = text.lower()
    for loc in MALAWI_LOCATIONS.keys():
        if loc in text:
            return loc.title()
            
    return None
