# AgriAssist - Complete Authentication & Session Implementation

## Overview
Your AgriAssist chatbot application has been fully updated with:
- ✅ User authentication (signup/login/logout)
- ✅ Session management with chat history
- ✅ User profiles with location and specialization
- ✅ Integration with 6 agricultural data APIs
- ✅ LLM-powered chatbot with API context

## Key Features Implemented

### 1. Authentication System
- **Signup**: Users can create accounts with username, email, password, location, and specialization
- **Login**: Secure session-based authentication
- **Logout**: Secure session termination
- **Session Management**: Django session middleware for persistent user sessions

### 2. User Management
- **UserProfile Model**: Extended Django User with location and specialization fields
- **ChatSession Model**: Tracks conversation sessions per user
- **ChatMessage Model**: Stores individual messages with timestamps

### 3. API Integration
The chatbot fetches agricultural data from:
1. `https://www.masdap.mw/geoserver/ows?service=WMS&version=1.1.1&request=GetCapabilities`
2. `https://www.masdap.mw/api/datasets/`
3. `https://www.masdap.mw/catalogue/csw?mode=oaipmh&verb=Identify`
4. `https://www.masdap.mw/catalogue/csw?mode=opensearch&service=CSW&version=2.0.2&request=GetCapabilities`
5. `https://wfp-malawi-gis-hub-unwfp.hub.arcgis.com/api/feed/dcat-us/1.1.json`
6. `https://wfp-malawi-gis-hub-unwfp.hub.arcgis.com/api/feed/dcat-ap/2.0.1.json`

### 4. Chatbot Features
- Enhanced LLM prompts with agricultural API data
- Chat history persistence per user
- Session-based conversation management
- Automatic session titling based on first message

## File Structure Changes

```
AgriAssistant/
├── chatbot/
│   ├── models.py (UPDATED)
│   │   ├── UserProfile (NEW)
│   │   ├── ChatSession (NEW)
│   │   ├── ChatMessage (NEW)
│   │   └── [existing models preserved]
│   ├── views.py (UPDATED)
│   │   ├── signup() - User registration
│   │   ├── signin() - User login
│   │   ├── signout() - User logout
│   │   ├── chatbot_home() - Protected chatbot interface
│   │   ├── chatbot_api() - Chat API with auth & session
│   │   ├── get_session_messages() - Retrieve chat history
│   │   └── delete_session() - Delete chat sessions
│   ├── urls.py (UPDATED)
│   │   ├── /signup/ - Signup page
│   │   ├── /signin/ - Login page
│   │   ├── /logout/ - Logout endpoint
│   │   ├── / - Chatbot interface (protected)
│   │   ├── /api/ - Chat API (protected)
│   │   ├── /session/<id>/ - Get messages
│   │   └── /session/<id>/delete/ - Delete session
│   └── utils.py (UPDATED)
│       ├── fetch_api_data() - Fetch from agricultural APIs
│       ├── format_api_data_for_context() - Format for LLM
│       └── query_mistral_llm() - Updated with API context
├── templates/
│   ├── signup.html (NEW) - User registration UI
│   ├── login.html (UPDATED) - Login UI with new design
│   └── chatbot.html (UPDATED) - Chatbot with sidebar, history, user info
├── AgriAssistant/
│   ├── settings.py (UPDATED)
│   │   ├── Added 'rest_framework' to INSTALLED_APPS
│   │   ├── Session configuration
│   │   └── Login/Logout URL settings
│   └── urls.py (unchanged)
├── requirements.txt (NEW)
└── migrations/
    └── 0002_chatsession_chatmessage_userprofile.py (AUTO-GENERATED)
```

## Database Models

### UserProfile
```python
user = OneToOneField(User)  # Links to Django User
location = CharField       # User's location (optional)
specialization = CharField # Area of expertise (optional)
created_at = DateTimeField
updated_at = DateTimeField
```

### ChatSession
```python
user = ForeignKey(User)    # Which user owns this session
created_at = DateTimeField
updated_at = DateTimeField
title = CharField          # Auto-generated from first message
```

### ChatMessage
```python
session = ForeignKey(ChatSession)
user_message = TextField   # User's question
bot_response = TextField   # Chatbot's answer
created_at = DateTimeField
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
- **Signup**: `http://localhost:8000/chatbot/signup/`
- **Login**: `http://localhost:8000/chatbot/signin/`
- **Chatbot**: `http://localhost:8000/chatbot/` (after login)

## API Endpoints

### Authentication Endpoints
- `POST /chatbot/signup/` - Register new user
- `POST /chatbot/signin/` - Login user
- `GET /chatbot/logout/` - Logout user

### Chatbot Endpoints (Requires Authentication)
- `GET /chatbot/` - Render chatbot interface
- `POST /chatbot/api/` - Send chat message
  - Request: `{"question": "...", "session_id": null|id}`
  - Response: `{"response": "...", "session_id": id, "message_id": id}`
- `GET /chatbot/session/<id>/` - Get session messages
- `POST /chatbot/session/<id>/delete/` - Delete session

## Authentication Flow

1. **Signup**: User creates account → UserProfile auto-created → Redirects to chatbot
2. **Login**: User authenticates → Django session created → Access chatbot
3. **Session**: Each request includes CSRF token + session cookie
4. **Logout**: Session destroyed, redirects to login
5. **Protected Views**: `@login_required` decorator ensures auth

## API Data Integration

### Fetch Process (Per Chat Message)
1. User sends question via chatbot
2. `fetch_api_data()` queries all 6 endpoints (30-second timeout)
3. `format_api_data_for_context()` summarizes the data
4. Formatted API data added to LLM system prompt
5. LLM generates response with API context
6. Response + message saved to database

### Error Handling
- Timeouts: Gracefully handled, requests marked as error
- Connection issues: Logged and skipped
- Invalid JSON: Only JSON endpoints parsed fully
- Large responses: Automatically truncated to prevent token overflow

## Security Features

✅ **CSRF Protection**: All forms include CSRF tokens
✅ **Session Security**: HttpOnly cookies, 2-week session timeout
✅ **Authentication**: Login required for chatbot access
✅ **Password Security**: Django's built-in password validation
✅ **SQL Injection**: Django ORM prevents SQL attacks
✅ **XSS Protection**: Template auto-escaping enabled

## Configuration Notes

### Session Settings (in settings.py)
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
```

### API Timeout
```python
API_TIMEOUT = 30  # seconds
```

### HTTPS/Production
Before deploying to production:
1. Set `DEBUG = False` in settings.py
2. Set `CSRF_COOKIE_SECURE = True`
3. Set `SESSION_COOKIE_SECURE = True`
4. Update `ALLOWED_HOSTS` with your domain
5. Use environment variables for `SECRET_KEY`

## Testing the Application

### Test Signup
```bash
# POST to /chatbot/signup/
{
  "username": "farmer1",
  "email": "farmer@example.com",
  "password": "secure_password",
  "location": "Lilongwe District",
  "specialization": "Crop Management"
}
```

### Test Chatbot API
```bash
# POST to /chatbot/api/ (with authentication)
{
  "question": "What is the best fertilizer for maize?",
  "session_id": null
}
```

## Troubleshooting

### Issues with API calls timing out?
- Increase `API_TIMEOUT` in settings.py
- Check internet connectivity
- Verify API endpoints are accessible

### Session not persisting?
- Ensure `SessionMiddleware` is in MIDDLEWARE
- Check browser cookies are enabled
- Verify database is properly configured

### Users not finding chat history?
- Chat history loads after first message
- Sessions are created per conversation
- Use `/chatbot/session/<id>/` to fetch messages

## Next Steps

### Recommended Enhancements
1. Add chat search/filter functionality
2. Implement admin panel for managing users and chat data
3. Add export chat history as PDF/CSV
4. Implement rate limiting on API calls
5. Add WebSocket support for real-time chat
6. Create mobile app with authentication
7. Add advanced analytics on chatbot usage
8. Implement caching for API responses
9. Add user preferences (theme, language, etc.)
10. Create admin dashboard for monitoring chats

## Support

For issues or questions:
1. Check Django documentation: https://docs.djangoproject.com/
2. Review the code comments in views.py and utils.py
3. Check API endpoints directly in browser/postman
4. View Django logs for detailed error messages

---

**Last Updated**: November 19, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready (with HTTPS configuration)
