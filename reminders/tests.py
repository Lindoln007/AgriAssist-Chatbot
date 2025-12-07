"""
Comprehensive test suite for the reminders app.
Tests models, views, and API endpoints.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time, timedelta
import json
from .models import FarmReminder


class FarmReminderModelTest(TestCase):
    """Test FarmReminder model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_farm_reminder_creation(self):
        """Test FarmReminder creation"""
        reminder = FarmReminder.objects.create(
            user=self.user,
            activity_type='Planting',
            crop_or_livestock='Maize',
            date=date.today(),
            time=time(8, 0),
            notes='Plant in rows',
            status='pending'
        )
        self.assertEqual(reminder.user, self.user)
        self.assertEqual(reminder.activity_type, 'Planting')
        self.assertEqual(reminder.status, 'pending')
        self.assertIsNotNone(reminder.created_at)
    
    def test_farm_reminder_str(self):
        """Test FarmReminder string representation"""
        reminder = FarmReminder.objects.create(
            user=self.user,
            activity_type='Harvesting',
            crop_or_livestock='Tomatoes',
            date=date.today(),
            time=time(9, 0)
        )
        self.assertIn('Harvesting', str(reminder))
        self.assertIn('Tomatoes', str(reminder))
    
    def test_farm_reminder_default_status(self):
        """Test that reminder defaults to pending status"""
        reminder = FarmReminder.objects.create(
            user=self.user,
            activity_type='Watering',
            crop_or_livestock='Beans',
            date=date.today()
        )
        self.assertEqual(reminder.status, 'pending')
    
    def test_farm_reminder_ordering(self):
        """Test that reminders are ordered by date and time"""
        reminder1 = FarmReminder.objects.create(
            user=self.user,
            activity_type='First',
            crop_or_livestock='Crop1',
            date=date.today() + timedelta(days=1),
            time=time(10, 0)
        )
        reminder2 = FarmReminder.objects.create(
            user=self.user,
            activity_type='Second',
            crop_or_livestock='Crop2',
            date=date.today(),
            time=time(8, 0)
        )
        reminders = list(FarmReminder.objects.all())
        self.assertEqual(reminders[0].activity_type, 'Second')


class RemindersViewsTest(TestCase):
    """Test reminders views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.index_url = reverse('reminders:index')
        self.add_url = reverse('reminders:add')
        self.api_url = reverse('reminders:api_events')
    
    def test_index_requires_login(self):
        """Test that reminders index requires authentication"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_index_authenticated(self):
        """Test reminders index page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('reminders', response.context)
    
    def test_add_reminder_success(self):
        """Test adding a new reminder"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'activity_type': 'Planting',
            'crop_or_livestock': 'Maize',
            'date': str(date.today()),
            'time': '08:00',
            'notes': 'Plant in rows'
        }
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(FarmReminder.objects.filter(
            user=self.user,
            activity_type='Planting'
        ).exists())
    
    def test_add_reminder_missing_fields(self):
        """Test adding reminder with missing required fields"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'activity_type': 'Planting'
        }
        response = self.client.post(self.add_url, data)
        # Should still redirect but reminder won't be created
        self.assertFalse(FarmReminder.objects.filter(
            user=self.user,
            activity_type='Planting'
        ).exists())
    
    def test_update_status_to_completed(self):
        """Test updating reminder status to completed"""
        self.client.login(username='testuser', password='testpass123')
        reminder = FarmReminder.objects.create(
            user=self.user,
            activity_type='Watering',
            crop_or_livestock='Beans',
            date=date.today(),
            status='pending'
        )
        url = reverse('reminders:update_status', args=[reminder.id])
        response = self.client.post(url, {'status': 'completed'})
        self.assertEqual(response.status_code, 302)  # Redirect
        reminder.refresh_from_db()
        self.assertEqual(reminder.status, 'completed')
    
    def test_update_status_to_pending(self):
        """Test updating reminder status back to pending"""
        self.client.login(username='testuser', password='testpass123')
        reminder = FarmReminder.objects.create(
            user=self.user,
            activity_type='Harvesting',
            crop_or_livestock='Tomatoes',
            date=date.today(),
            status='completed'
        )
        url = reverse('reminders:update_status', args=[reminder.id])
        response = self.client.post(url, {'status': 'pending'})
        reminder.refresh_from_db()
        self.assertEqual(reminder.status, 'pending')
    
    def test_update_status_not_owner(self):
        """Test that users cannot update other users' reminders"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        reminder = FarmReminder.objects.create(
            user=other_user,
            activity_type='Planting',
            crop_or_livestock='Maize',
            date=date.today()
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('reminders:update_status', args=[reminder.id])
        response = self.client.post(url, {'status': 'completed'})
        self.assertEqual(response.status_code, 404)
    
    def test_api_events_requires_login(self):
        """Test that API events endpoint requires authentication"""
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_api_events_returns_json(self):
        """Test API events endpoint returns JSON"""
        self.client.login(username='testuser', password='testpass123')
        FarmReminder.objects.create(
            user=self.user,
            activity_type='Planting',
            crop_or_livestock='Maize',
            date=date.today(),
            time=time(8, 0)
        )
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIn('title', data[0])
        self.assertIn('start', data[0])
    
    def test_api_events_only_user_reminders(self):
        """Test that API only returns current user's reminders"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        FarmReminder.objects.create(
            user=other_user,
            activity_type='Other User Reminder',
            crop_or_livestock='Crop',
            date=date.today()
        )
        FarmReminder.objects.create(
            user=self.user,
            activity_type='My Reminder',
            crop_or_livestock='My Crop',
            date=date.today()
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_url)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertIn('My Reminder', data[0]['title'])
    
    def test_api_events_color_coding(self):
        """Test that API returns correct colors for different statuses"""
        self.client.login(username='testuser', password='testpass123')
        
        # Pending reminder
        pending = FarmReminder.objects.create(
            user=self.user,
            activity_type='Pending',
            crop_or_livestock='Crop1',
            date=date.today(),
            status='pending'
        )
        
        # Completed reminder
        completed = FarmReminder.objects.create(
            user=self.user,
            activity_type='Completed',
            crop_or_livestock='Crop2',
            date=date.today(),
            status='completed'
        )
        
        # Overdue reminder
        overdue = FarmReminder.objects.create(
            user=self.user,
            activity_type='Overdue',
            crop_or_livestock='Crop3',
            date=date.today() - timedelta(days=1),
            status='pending'
        )
        
        response = self.client.get(self.api_url)
        data = json.loads(response.content)
        
        # Find reminders in response
        pending_event = next((e for e in data if 'Pending' in e['title']), None)
        completed_event = next((e for e in data if 'Completed' in e['title']), None)
        overdue_event = next((e for e in data if 'Overdue' in e['title']), None)
        
        self.assertIsNotNone(pending_event)
        self.assertIsNotNone(completed_event)
        self.assertIsNotNone(overdue_event)
        
        # Check colors (yellow for pending, green for completed, red for overdue)
        self.assertEqual(completed_event['backgroundColor'], '#2F855A')
        self.assertEqual(overdue_event['backgroundColor'], '#E53E3E')
