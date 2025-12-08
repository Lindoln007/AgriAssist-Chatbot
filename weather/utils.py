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

def get_weather_forecast(lat, lon, days=7):
    """
    Fetch weather forecast from Open-Meteo API.

    Parameters:
    - lat, lon: coordinates
    - days: number of days of forecast to request (default 7)

    Returns the parsed JSON response from Open-Meteo (may include 'current_weather',
    'hourly' and 'daily' sections depending on requested params).
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        # Request hourly details and daily summaries for the requested number of days
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,cloudcover,windspeed_10m,soil_moisture_0_1cm",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "forecast_days": int(days),
            "current_weather": "true",
            "timezone": "auto"
        }

        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def analyze_weather_for_farming(weather_data):
    """
    Analyze weather data and provide farming recommendations.

    Uses `daily` summaries when available to produce multi-day insights and
    actionable recommendations. Falls back to `current_weather` and hourly
    values when daily summaries are not provided.
    """
    if not weather_data:
        return "Weather data unavailable for analysis."

    recommendations = []

    # Prefer daily summaries for multi-day planning
    daily = weather_data.get('daily', {})
    current = weather_data.get('current_weather', {})
    hourly = weather_data.get('hourly', {})

    # Helper defaults
    today_temp = current.get('temperature') if current else None
    today_wind = current.get('windspeed') if current else None

    if daily and 'time' in daily:
        times = daily.get('time', [])
        tmax = daily.get('temperature_2m_max', [])
        tmin = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        windmax = daily.get('windspeed_10m_max', [])

        # Summarize 3-day outlook (or fewer if less data)
        days_to_show = min(3, len(times))
        summary_lines = []
        heavy_rain_days = 0
        heat_alert_days = 0
        cold_alert_days = 0

        for i in range(days_to_show):
            day = times[i]
            max_t = tmax[i] if i < len(tmax) else None
            min_t = tmin[i] if i < len(tmin) else None
            p = precip[i] if i < len(precip) else 0
            w = windmax[i] if i < len(windmax) else None

            # Simple classification
            rain_label = 'No significant rain' if (p is None or p < 1) else f'Expected {p:.1f} mm rain'
            temp_label = ''
            if max_t is not None and min_t is not None:
                temp_label = f'{min_t:.0f}–{max_t:.0f}°C'
                if max_t >= 35:
                    heat_alert_days += 1
                if min_t <= 5:
                    cold_alert_days += 1
            if p and p >= 10:
                heavy_rain_days += 1

            summary_lines.append(f'- {day}: {temp_label}; {rain_label}' + (f'; wind up to {w:.0f} km/h' if w else ''))

        # Top-level summary
        recommendations.append('**3‑Day Outlook:**')
        recommendations.extend(summary_lines)

        # Irrigation advice over multi-day window
        if heavy_rain_days >= 2:
            recommendations.append('🌧️ <strong>Irrigation:</strong> Multiple heavy rain days expected. Suspend irrigation and improve drainage where waterlogging is possible.')
        elif heavy_rain_days == 1:
            recommendations.append('💧 <strong>Irrigation:</strong> Some rain expected; check soil moisture before irrigating. Prefer irrigation early morning if needed.')
        else:
            # Estimate soil moisture from precip + temps (best-effort)
            avg_precip = sum(precip[:days_to_show]) / max(1, days_to_show)
            if avg_precip < 1:
                recommendations.append('💧 <strong>Irrigation:</strong> Low rainfall expected. Schedule irrigation in the early morning to reduce evaporation.')
            else:
                recommendations.append('✅ <strong>Irrigation:</strong> Rainfall and conditions look adequate for the next few days.')

        # Field work and spraying guidance
        if any((p and p >= 5) for p in precip[:days_to_show]):
            recommendations.append('🚜 <strong>Field Work:</strong> Expect rain; avoid pesticide/fertilizer applications on wet days. Plan mechanical work on drier windows.')
        elif any((w and w >= 25) for w in windmax[:days_to_show]):
            recommendations.append('💨 <strong>Spraying:</strong> High winds expected on some days. Avoid spraying to reduce drift and uneven application.')
        else:
            recommendations.append('🌱 <strong>Field Work:</strong> Conditions look suitable for planting, weeding and applications during dry windows.')

        # Pest & disease risk
        # Use humidity approximation from hourly if available, otherwise use temp/precip heuristics
        avg_humidity = None
        if 'relative_humidity_2m' in hourly and hourly.get('relative_humidity_2m'):
            try:
                avg_humidity = sum(hourly['relative_humidity_2m']) / len(hourly['relative_humidity_2m'])
            except Exception:
                avg_humidity = None

        if avg_humidity and avg_humidity > 80 and (today_temp and today_temp > 20):
            recommendations.append('🐛 <strong>Pests & Disease:</strong> High humidity with warm temperatures increases fungal disease risk. Consider scouting and targeted fungicide if symptoms appear.')
        elif heavy_rain_days >= 1 and (today_temp and today_temp > 18):
            recommendations.append('🐜 <strong>Pests & Disease:</strong> Rainy warm periods can increase pest activity — increase monitoring frequency.')
        else:
            recommendations.append('🔍 <strong>Pests & Disease:</strong> Maintain routine scouting; no immediate elevated risk detected.')

        # Heat / Cold alerts for livestock and crops
        if heat_alert_days > 0:
            recommendations.append('🔥 <strong>Heat Alert:</strong> High daytime temperatures expected on some days. Provide shade and extra water for livestock and avoid field labor during peak heat.')
        if cold_alert_days > 0:
            recommendations.append('❄️ <strong>Cold Alert:</strong> Low night temperatures expected. Protect sensitive seedlings and young livestock.')

        return "\n\n".join(recommendations)

    # --- Fallback: hourly / current-based recommendations (previous behavior) ---
    temp = today_temp
    wind_speed = today_wind

    precip_prob = 0
    avg_humidity = 0
    avg_soil_moisture = 0

    if hourly:
        if 'precipitation' in hourly and hourly.get('precipitation'):
            total_precip = sum(hourly['precipitation'])
            precip_prob = 100 if total_precip > 0.5 else 0
        if 'relative_humidity_2m' in hourly and hourly.get('relative_humidity_2m'):
            try:
                avg_humidity = sum(hourly['relative_humidity_2m']) / len(hourly['relative_humidity_2m'])
            except Exception:
                avg_humidity = 0
        if 'soil_moisture_0_1cm' in hourly and hourly.get('soil_moisture_0_1cm'):
            try:
                avg_soil_moisture = sum(hourly['soil_moisture_0_1cm']) / len(hourly['soil_moisture_0_1cm'])
            except Exception:
                avg_soil_moisture = 0

    # 1. Irrigation Advice
    if precip_prob > 50:
        recommendations.append("🌧️ <strong>Irrigation:</strong> Rain is expected. Suspend irrigation to save water and prevent waterlogging.")
    elif avg_soil_moisture and avg_soil_moisture < 0.2:
        recommendations.append("💧 <strong>Irrigation:</strong> Soil moisture is low. Irrigation is recommended, preferably in the early morning or late afternoon.")
    else:
        recommendations.append("✅ <strong>Irrigation:</strong> Soil moisture levels are adequate. No immediate irrigation needed.")

    # 2. Field Work / Spraying
    if precip_prob > 20:
        recommendations.append("🚜 <strong>Field Work:</strong> Avoid applying fertilizers or pesticides today as rain may wash them away. Delay harvesting to prevent crop spoilage.")
    elif wind_speed and wind_speed > 20:
        recommendations.append("💨 <strong>Spraying:</strong> High wind speeds detected. Avoid spraying pesticides to prevent drift.")
    else:
        recommendations.append("🌱 <strong>Field Work:</strong> Conditions are favorable for planting, weeding, and applying fertilizers.")

    # 3. Pest & Disease
    if avg_humidity and avg_humidity > 80 and temp and temp > 20:
        recommendations.append("🐛 <strong>Pests & Disease:</strong> High humidity and warm temperatures favor fungal diseases like blight. Monitor crops closely.")
    else:
        recommendations.append("🔍 <strong>Pests & Disease:</strong> Continue routine scouting.")

    # 4. Livestock
    if temp and temp > 30:
        recommendations.append("🐄 <strong>Livestock:</strong> High temperatures expected. Ensure animals have plenty of shade and water to prevent heat stress.")
    elif temp and temp < 15:
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
