"""
Comprehensive test suite for the policy_updates app.
Tests models, views, and admin functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from .models import GovUpdate


class GovUpdateModelTest(TestCase):
    """Test GovUpdate model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
    
    def test_gov_update_creation(self):
        """Test GovUpdate creation"""
        update = GovUpdate.objects.create(
            title='New Subsidy Program',
            category='subsidy',
            content='Details about the subsidy program',
            date_posted=date.today(),
            created_by=self.user
        )
        self.assertEqual(update.title, 'New Subsidy Program')
        self.assertEqual(update.category, 'subsidy')
        self.assertEqual(update.created_by, self.user)
        self.assertIsNotNone(update.created_at)
    
    def test_gov_update_str(self):
        """Test GovUpdate string representation"""
        update = GovUpdate.objects.create(
            title='Policy Update',
            category='policy',
            content='Policy details',
            date_posted=date.today(),
            created_by=self.user
        )
        self.assertIn('Policy Update', str(update))
        self.assertIn('Policy', str(update))
    
    def test_gov_update_ordering(self):
        """Test that updates are ordered by date_posted descending"""
        update1 = GovUpdate.objects.create(
            title='Older Update',
            category='policy',
            content='Content',
            date_posted=date.today() - timedelta(days=1),
            created_by=self.user
        )
        update2 = GovUpdate.objects.create(
            title='Newer Update',
            category='policy',
            content='Content',
            date_posted=date.today(),
            created_by=self.user
        )
        updates = list(GovUpdate.objects.all())
        self.assertEqual(updates[0].title, 'Newer Update')


class PolicyUpdatesViewsTest(TestCase):
    """Test policy updates views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.update = GovUpdate.objects.create(
            title='Test Update',
            category='policy',
            content='Test content',
            date_posted=date.today(),
            created_by=self.admin
        )
    
    def test_user_list_requires_login(self):
        """Test that user list requires authentication"""
        url = reverse('policy_updates:user_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_list_authenticated(self):
        """Test user list page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:user_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('updates', response.context)
    
    def test_user_list_filter_by_category(self):
        """Test filtering updates by category"""
        GovUpdate.objects.create(
            title='Subsidy Update',
            category='subsidy',
            content='Content',
            date_posted=date.today(),
            created_by=self.admin
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:user_list')
        response = self.client.get(url, {'category': 'subsidy'})
        self.assertEqual(response.status_code, 200)
        updates = response.context['updates']
        self.assertTrue(all(u.category == 'subsidy' for u in updates))
    
    def test_user_list_search(self):
        """Test searching updates by keyword"""
        GovUpdate.objects.create(
            title='Maize Farming Guide',
            category='policy',
            content='Guide content',
            date_posted=date.today(),
            created_by=self.admin
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:user_list')
        response = self.client.get(url, {'search': 'Maize'})
        self.assertEqual(response.status_code, 200)
        updates = response.context['updates']
        self.assertTrue(any('Maize' in u.title for u in updates))
    
    def test_user_detail_requires_login(self):
        """Test that user detail requires authentication"""
        url = reverse('policy_updates:user_detail', args=[self.update.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_detail_authenticated(self):
        """Test user detail page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:user_detail', args=[self.update.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('update', response.context)
        self.assertEqual(response.context['update'], self.update)
    
    def test_user_detail_marks_new_updates(self):
        """Test that updates posted within 7 days are marked as new"""
        new_update = GovUpdate.objects.create(
            title='New Update',
            category='policy',
            content='Content',
            date_posted=date.today(),
            created_by=self.admin
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:user_detail', args=[new_update.pk])
        response = self.client.get(url)
        self.assertTrue(response.context['is_new'])
    
    def test_admin_list_requires_staff(self):
        """Test that admin list requires staff privileges"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:admin_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect (403)
    
    def test_admin_list_staff_access(self):
        """Test admin list page for staff users"""
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('updates', response.context)
    
    def test_admin_create_requires_staff(self):
        """Test that admin create requires staff privileges"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:admin_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect (403)
    
    def test_admin_create_get(self):
        """Test admin create page (GET)"""
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_admin_create_post(self):
        """Test creating a new update via admin form"""
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_create')
        data = {
            'title': 'New Policy',
            'category': 'policy',
            'content': 'Policy content here',
            'date_posted': str(date.today())
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(GovUpdate.objects.filter(title='New Policy').exists())
    
    def test_admin_edit_requires_staff(self):
        """Test that admin edit requires staff privileges"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:admin_edit', args=[self.update.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect (403)
    
    def test_admin_edit_get(self):
        """Test admin edit page (GET)"""
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_edit', args=[self.update.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('update', response.context)
    
    def test_admin_edit_post(self):
        """Test editing an update via admin form"""
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_edit', args=[self.update.pk])
        data = {
            'title': 'Updated Title',
            'category': 'policy',
            'content': 'Updated content',
            'date_posted': str(date.today())
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.update.refresh_from_db()
        self.assertEqual(self.update.title, 'Updated Title')
    
    def test_admin_delete_requires_staff(self):
        """Test that admin delete requires staff privileges"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('policy_updates:admin_delete', args=[self.update.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect (403)
    
    def test_admin_delete_get(self):
        """Test admin delete confirmation page (GET)"""
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_delete', args=[self.update.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('update', response.context)
    
    def test_admin_delete_post(self):
        """Test deleting an update"""
        update_id = self.update.pk
        self.client.login(username='admin', password='adminpass')
        url = reverse('policy_updates:admin_delete', args=[update_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertFalse(GovUpdate.objects.filter(pk=update_id).exists())
