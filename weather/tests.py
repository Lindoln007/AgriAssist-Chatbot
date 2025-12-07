"""
Comprehensive test suite for the weather app.
Tests views and utility functions.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from chatbot.models import UserProfile


class WeatherViewsTest(TestCase):
    """Test weather views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            location='Lilongwe'
        )
        self.index_url = reverse('weather:index')
        self.api_url = reverse('weather:api_get_weather')
    
    def test_index_requires_login(self):
        """Test that weather index requires authentication"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    @patch('weather.views.analyze_weather_for_farming')
    def test_index_authenticated(self, mock_analyze, mock_forecast, mock_coords):
        """Test weather index page for authenticated user"""
        # Mock responses
        mock_coords.return_value = {
            'name': 'Lilongwe',
            'lat': -13.9626,
            'lon': 33.7741
        }
        mock_forecast.return_value = {
            'current_weather': {
                'temperature': 25.0,
                'windspeed': 10.0,
                'winddirection': 180
            },
            'daily': {
                'time': ['2024-01-01', '2024-01-02'],
                'temperature_2m_max': [28.0, 29.0],
                'temperature_2m_min': [18.0, 19.0],
                'precipitation_sum': [0.0, 5.0],
                'windspeed_10m_max': [12.0, 13.0]
            }
        }
        mock_analyze.return_value = 'Good weather for farming'
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('weather', response.context)
        self.assertIn('location', response.context)
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    @patch('weather.views.analyze_weather_for_farming')
    def test_index_with_location_query(self, mock_analyze, mock_forecast, mock_coords):
        """Test weather index with location query parameter"""
        mock_coords.return_value = {
            'name': 'Blantyre',
            'lat': -15.7845,
            'lon': 35.0054
        }
        mock_forecast.return_value = {
            'current_weather': {'temperature': 24.0}
        }
        mock_analyze.return_value = 'Weather analysis'
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.index_url, {'location': 'Blantyre'})
        self.assertEqual(response.status_code, 200)
        # Check that location override is set in session
        self.assertEqual(self.client.session.get('weather_override'), 'Blantyre')
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    @patch('weather.views.analyze_weather_for_farming')
    def test_index_save_location(self, mock_analyze, mock_forecast, mock_coords):
        """Test saving location to user profile"""
        mock_coords.return_value = {
            'name': 'Mzuzu',
            'lat': -11.4587,
            'lon': 34.0151
        }
        mock_forecast.return_value = {
            'current_weather': {'temperature': 22.0}
        }
        mock_analyze.return_value = 'Weather analysis'
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.index_url, {
            'save': '1',
            'save_location': 'Mzuzu'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.location, 'Mzuzu')
        # Check that override is cleared
        self.assertIsNone(self.client.session.get('weather_override'))
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    @patch('weather.views.analyze_weather_for_farming')
    def test_index_clear_override(self, mock_analyze, mock_forecast, mock_coords):
        """Test clearing location override"""
        mock_coords.return_value = {
            'name': 'Lilongwe',
            'lat': -13.9626,
            'lon': 33.7741
        }
        mock_forecast.return_value = {
            'current_weather': {'temperature': 25.0}
        }
        mock_analyze.return_value = 'Weather analysis'
        
        self.client.login(username='testuser', password='testpass123')
        # Set override first
        session = self.client.session
        session['weather_override'] = 'Blantyre'
        session.save()
        
        response = self.client.post(self.index_url, {'clear_override': '1'})
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIsNone(self.client.session.get('weather_override'))
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    @patch('weather.views.analyze_weather_for_farming')
    def test_index_location_not_found(self, mock_analyze, mock_forecast, mock_coords):
        """Test handling when location is not found"""
        # When location is not found, it falls back to Lilongwe
        def coords_side_effect(location):
            if location == 'InvalidLocation':
                return None
            return {
                'name': 'Lilongwe',
                'lat': -13.9626,
                'lon': 33.7741
            }
        mock_coords.side_effect = coords_side_effect
        mock_forecast.return_value = {
            'current_weather': {'temperature': 25.0}
        }
        mock_analyze.return_value = 'Weather analysis'
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.index_url, {'location': 'InvalidLocation'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
    
    def test_api_get_weather_requires_login(self):
        """Test that API weather endpoint requires authentication"""
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_api_get_weather_missing_location(self):
        """Test API with missing location parameter"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('weather.views.get_coordinates')
    def test_api_get_weather_location_not_found(self, mock_coords):
        """Test API when location is not found"""
        mock_coords.return_value = None
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_url, {'location': 'InvalidLocation'})
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    @patch('weather.views.analyze_weather_for_farming')
    def test_api_get_weather_success(self, mock_analyze, mock_forecast, mock_coords):
        """Test successful API weather request"""
        mock_coords.return_value = {
            'name': 'Lilongwe',
            'lat': -13.9626,
            'lon': 33.7741
        }
        mock_forecast.return_value = {
            'current_weather': {
                'temperature': 25.0,
                'windspeed': 10.0,
                'winddirection': 180
            }
        }
        mock_analyze.return_value = 'Good weather for farming'
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_url, {'location': 'Lilongwe'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('location', data)
        self.assertIn('coordinates', data)
        self.assertIn('current', data)
        self.assertIn('analysis', data)
    
    @patch('weather.views.get_coordinates')
    @patch('weather.views.get_weather_forecast')
    def test_api_get_weather_service_unavailable(self, mock_forecast, mock_coords):
        """Test API when weather service is unavailable"""
        mock_coords.return_value = {
            'name': 'Lilongwe',
            'lat': -13.9626,
            'lon': 33.7741
        }
        mock_forecast.return_value = None
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_url, {'location': 'Lilongwe'})
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertIn('error', data)
