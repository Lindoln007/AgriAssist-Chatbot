from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import get_coordinates, get_weather_forecast, analyze_weather_for_farming
from chatbot.models import UserProfile
from datetime import datetime as _dt
import re

@login_required
def index(request):
    """
    Weather dashboard view.
    """
    # Handle POST actions: saving a district to profile or clearing session override
    if request.method == 'POST':
        # Save the currently viewed location as the user's saved district
        if request.POST.get('save'):
            save_location = request.POST.get('save_location')
            try:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.location = save_location or profile.location
                profile.save()
            except Exception:
                pass
            # Clear any temporary override after saving
            request.session.pop('weather_override', None)
            return redirect('weather:index')

        # Clear temporary override and return to saved district
        if request.POST.get('clear_override'):
            request.session.pop('weather_override', None)
            return redirect('weather:index')

    # Default to Lilongwe if no location specified or found in user profile
    default_location = "Lilongwe"
    try:
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile and profile.location:
            default_location = profile.location
    except Exception:
        default_location = "Lilongwe"

    # If a location was provided via GET, treat it as a temporary override (session-scoped)
    location_query = request.GET.get('location')
    if location_query:
        # store override in session so other modules (chatbot) can respect it
        request.session['weather_override'] = location_query
    else:
        # If no explicit GET param, prefer any active session override
        location_query = request.session.get('weather_override', default_location)
    coords = get_coordinates(location_query)
    
    weather_data = None
    analysis = None
    error = None
    
    if coords:
        weather_data = get_weather_forecast(coords['lat'], coords['lon'])
        if weather_data:
            analysis = analyze_weather_for_farming(weather_data)
            # Convert analysis string (which may contain markdown-like markers) into simple HTML
            def analysis_to_html(text):
                if not text:
                    return ''
                # convert **bold** markers to <strong>
                text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
                lines = text.splitlines()
                out = []
                in_list = False
                for line in lines:
                    line = line.rstrip()
                    if line.startswith('- '):
                        if not in_list:
                            out.append('<ul style="margin:8px 0 12px 18px;">')
                            in_list = True
                        out.append(f"<li>{line[2:].strip()}</li>")
                    else:
                        if in_list:
                            out.append('</ul>')
                            in_list = False
                        if line.strip() == '':
                            continue
                        # keep lines that already contain HTML tags
                        out.append(f"<p style=\"margin:8px 0;\">{line.strip()}</p>")
                if in_list:
                    out.append('</ul>')
                return '\n'.join(out)

            analysis = analysis_to_html(analysis)
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
        'current_date': datetime.now(),
        'override_active': bool(request.session.get('weather_override')),
        'override_value': request.session.get('weather_override') if request.session.get('weather_override') else None,
        # Build simple daily_list for template (up to 7 days)
        'daily_list': []
    }
    # populate daily_list if available
    if weather_data and 'daily' in weather_data:
        daily = weather_data.get('daily', {})
        times = daily.get('time', [])
        tmax = daily.get('temperature_2m_max', [])
        tmin = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        wind = daily.get('windspeed_10m_max', [])

        daily_list = []
        for i, d in enumerate(times[:7]):
            # format date string (YYYY-MM-DD) into short weekday label (e.g., Mon)
            label = d
            try:
                label = _dt.strptime(d, '%Y-%m-%d').strftime('%a')
            except Exception:
                label = d
            daily_list.append({
                'date': label,
                'tmax': tmax[i] if i < len(tmax) else None,
                'tmin': tmin[i] if i < len(tmin) else None,
                'precip': precip[i] if i < len(precip) else None,
                'wind': wind[i] if i < len(wind) else None,
            })
        context['daily_list'] = daily_list

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
