"""
Comprehensive test suite for the chatbot app.
Tests authentication, views, models, and API endpoints.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import json
from unittest.mock import patch, MagicMock
from .models import UserProfile, ChatSession, ChatMessage, AgriculturalFAQ, PestInfo, FertilizerGuideline, CropManagementTip, ExtensionResource


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created correctly"""
        profile = UserProfile.objects.create(
            user=self.user,
            display_name='Test User',
            location='Lilongwe',
            specialization='Crop Management'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.display_name, 'Test User')
        self.assertEqual(profile.location, 'Lilongwe')
        self.assertEqual(profile.specialization, 'Crop Management')
    
    def test_user_profile_str(self):
        """Test UserProfile string representation"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertIn('testuser', str(profile))


class ChatSessionModelTest(TestCase):
    """Test ChatSession model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_chat_session_creation(self):
        """Test ChatSession creation"""
        session = ChatSession.objects.create(
            user=self.user,
            title='Test Chat'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.title, 'Test Chat')
        self.assertIsNotNone(session.created_at)
    
    def test_chat_session_ordering(self):
        """Test that sessions are ordered by updated_at descending"""
        session1 = ChatSession.objects.create(user=self.user, title='First')
        session2 = ChatSession.objects.create(user=self.user, title='Second')
        sessions = list(ChatSession.objects.all())
        self.assertEqual(sessions[0].title, 'Second')


class ChatMessageModelTest(TestCase):
    """Test ChatMessage model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.session = ChatSession.objects.create(user=self.user)
    
    def test_chat_message_creation(self):
        """Test ChatMessage creation"""
        message = ChatMessage.objects.create(
            session=self.session,
            user_message='Hello',
            bot_response='Hi there!'
        )
        self.assertEqual(message.session, self.session)
        self.assertEqual(message.user_message, 'Hello')
        self.assertEqual(message.bot_response, 'Hi there!')


class AgriculturalDataModelsTest(TestCase):
    """Test agricultural data models"""
    
    def test_agricultural_faq_creation(self):
        """Test AgriculturalFAQ creation"""
        faq = AgriculturalFAQ.objects.create(
            question='How to grow maize?',
            answer='Plant in rows with proper spacing.',
            category='crop_care'
        )
        self.assertEqual(faq.question, 'How to grow maize?')
        self.assertEqual(faq.category, 'crop_care')
    
    def test_pest_info_creation(self):
        """Test PestInfo creation"""
        pest = PestInfo.objects.create(
            name='Aphids',
            description='Small insects',
            symptoms='Yellow leaves',
            treatment='Use insecticide',
            prevention='Regular monitoring',
            category='insects'
        )
        self.assertEqual(pest.name, 'Aphids')
        self.assertEqual(pest.category, 'insects')
    
    def test_fertilizer_guideline_creation(self):
        """Test FertilizerGuideline creation"""
        guideline = FertilizerGuideline.objects.create(
            crop_type='Maize',
            fertilizer_type='NPK',
            application_rate='100kg/ha',
            timing='At planting',
            notes='Apply evenly'
        )
        self.assertEqual(guideline.crop_type, 'Maize')
    
    def test_crop_management_tip_creation(self):
        """Test CropManagementTip creation"""
        tip = CropManagementTip.objects.create(
            crop_type='Maize',
            tip_title='Watering Schedule',
            tip_content='Water twice daily',
            season='rainy'
        )
        self.assertEqual(tip.tip_title, 'Watering Schedule')
    
    def test_extension_resource_creation(self):
        """Test ExtensionResource creation"""
        resource = ExtensionResource.objects.create(
            title='Farming Guide',
            content='Complete guide to farming',
            resource_type='guide'
        )
        self.assertEqual(resource.title, 'Farming Guide')
        self.assertEqual(resource.resource_type, 'guide')


class AuthenticationTest(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('chatbot:signup')
        self.user_login_url = reverse('chatbot:user_login')
        self.admin_login_url = reverse('chatbot:admin_login')
        self.logout_url = reverse('chatbot:logout')
    
    def test_signup_get(self):
        """Test signup page loads"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
    
    def test_signup_post_success(self):
        """Test successful user signup"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'location': 'Lilongwe',
            'specialization': 'Crop Management'
        }
        response = self.client.post(
            self.signup_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())
    
    def test_signup_duplicate_username(self):
        """Test signup with duplicate username"""
        User.objects.create_user(username='existing', password='pass')
        data = {
            'username': 'existing',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(
            self.signup_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_signup_missing_fields(self):
        """Test signup with missing required fields"""
        data = {'username': 'testuser'}
        response = self.client.post(
            self.signup_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_user_login_get(self):
        """Test user login page loads"""
        response = self.client.get(self.user_login_url)
        self.assertEqual(response.status_code, 200)
    
    def test_user_login_success(self):
        """Test successful user login"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(
            self.user_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(
            self.user_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_user_login_admin_blocked(self):
        """Test that admin users cannot login via user login"""
        admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        data = {
            'username': 'admin',
            'password': 'adminpass'
        }
        response = self.client.post(
            self.user_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        data = {
            'username': 'admin',
            'password': 'adminpass'
        }
        response = self.client.post(
            self.admin_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_admin_login_non_admin_blocked(self):
        """Test that non-admin users cannot login via admin login"""
        user = User.objects.create_user(
            username='regular',
            password='regularpass'
        )
        data = {
            'username': 'regular',
            'password': 'regularpass'
        }
        response = self.client.post(
            self.admin_login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_logout(self):
        """Test logout functionality"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Redirect


class ChatbotViewsTest(TestCase):
    """Test chatbot views"""
    
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
        self.home_url = reverse('chatbot:home')
        self.api_url = reverse('chatbot:api')
    
    def test_chatbot_home_requires_login(self):
        """Test that chatbot home requires authentication"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_chatbot_home_authenticated(self):
        """Test chatbot home page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_profile', response.context)
    
    @patch('chatbot.views.query_mistral_llm')
    @patch('chatbot.views.fetch_api_data')
    @patch('chatbot.views.search_agricultural_data')
    def test_chatbot_api_success(self, mock_search, mock_fetch, mock_llm):
        """Test chatbot API endpoint with successful response"""
        self.client.login(username='testuser', password='testpass123')
        
        # Mock responses
        mock_search.return_value = []
        mock_fetch.return_value = {}
        mock_llm.return_value = 'This is a test response'
        
        data = {
            'question': 'How to grow maize?'
        }
        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('response', data)
        self.assertIn('session_id', data)
        
        # Verify session and message were created
        self.assertTrue(ChatSession.objects.filter(user=self.user).exists())
        session = ChatSession.objects.get(user=self.user)
        self.assertTrue(ChatMessage.objects.filter(session=session).exists())
    
    def test_chatbot_api_requires_login(self):
        """Test that chatbot API requires authentication"""
        data = {'question': 'Test question'}
        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_chatbot_api_missing_question(self):
        """Test chatbot API with missing question"""
        self.client.login(username='testuser', password='testpass123')
        data = {}
        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    @patch('chatbot.views.search_agricultural_data')
    def test_chatbot_api_faq_match(self, mock_search):
        """Test chatbot API when FAQ match is found"""
        self.client.login(username='testuser', password='testpass123')
        
        # Mock FAQ search to return a result
        mock_search.return_value = ['This is an FAQ answer']
        
        data = {
            'question': 'How to grow maize?'
        }
        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['source'], 'faq')
        self.assertEqual(data['response'], 'This is an FAQ answer')


class ChatSessionViewsTest(TestCase):
    """Test chat session views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.session = ChatSession.objects.create(
            user=self.user,
            title='Test Session'
        )
        self.message = ChatMessage.objects.create(
            session=self.session,
            user_message='Hello',
            bot_response='Hi!'
        )
    
    def test_get_session_messages(self):
        """Test getting messages from a session"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('chatbot:session_messages', args=[self.session.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('messages', data)
        self.assertEqual(len(data['messages']), 1)
    
    def test_get_session_messages_not_owner(self):
        """Test that users cannot access other users' sessions"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        self.client.login(username='otheruser', password='otherpass')
        url = reverse('chatbot:session_messages', args=[self.session.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_delete_session(self):
        """Test deleting a session"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('chatbot:delete_session', args=[self.session.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ChatSession.objects.filter(id=self.session.id).exists())
    
    def test_delete_session_not_owner(self):
        """Test that users cannot delete other users' sessions"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        self.client.login(username='otheruser', password='otherpass')
        url = reverse('chatbot:delete_session', args=[self.session.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
    
    def test_get_user_sessions(self):
        """Test getting all user sessions"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('chatbot:get_sessions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('sessions', data)
        self.assertEqual(len(data['sessions']), 1)
