from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import get_coordinates, get_weather_forecast, analyze_weather_for_farming

@login_required
def index(request):
    """
    Weather dashboard view.
    """
    # Default to Lilongwe if no location specified or found in user profile
    default_location = "Lilongwe"
    if hasattr(request.user, 'userprofile') and request.user.userprofile.location:
        default_location = request.user.userprofile.location

    location_query = request.GET.get('location', default_location)
    coords = get_coordinates(location_query)
    
    weather_data = None
    analysis = None
    error = None
    
    if coords:
        weather_data = get_weather_forecast(coords['lat'], coords['lon'])
        if weather_data:
            analysis = analyze_weather_for_farming(weather_data)
        else:
            error = "Could not fetch weather data from service."
    else:
        # Fallback to Lilongwe if search fails
        coords = get_coordinates("Lilongwe")
        weather_data = get_weather_forecast(coords['lat'], coords['lon'])
        analysis = analyze_weather_for_farming(weather_data)
        error = f"Location '{location_query}' not found. Showing Lilongwe instead."

    context = {
        'location': coords['name'] if coords else location_query,
        'weather': weather_data,
        'analysis': analysis,
        'error': error,
        'current_date': datetime.now()
    }
    return render(request, 'weather/index.html', context)

@login_required
def api_get_weather(request):
    """
    Internal API for chatbot to fetch weather.
    """
    location = request.GET.get('location', '')
    if not location:
        return JsonResponse({'error': 'Location required'}, status=400)
        
    coords = get_coordinates(location)
    if not coords:
        return JsonResponse({'error': 'Location not found in Malawi database'}, status=404)
        
    weather_data = get_weather_forecast(coords['lat'], coords['lon'])
    if not weather_data:
        return JsonResponse({'error': 'Weather service unavailable'}, status=503)
        
    analysis = analyze_weather_for_farming(weather_data)
    
    return JsonResponse({
        'location': coords['name'],
        'coordinates': coords,
        'current': weather_data.get('current_weather', {}),
        'analysis': analysis
    })
