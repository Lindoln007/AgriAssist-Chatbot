# AgriAssist - Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Start the Server
```bash
cd e:\Projects\AgriAssistant
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 2: Create an Account
1. Open browser: `http://localhost:8000/chatbot/signup/`
2. Fill in:
   - Username: `farmer1`
   - Email: `farmer@example.com`
   - Password: `YourSecurePassword123`
   - Location: `Lilongwe` (optional)
   - Specialization: `Crop Management` (optional)
3. Click "Sign Up"

### Step 3: Start Chatting
1. You'll be redirected to the chatbot
2. Try asking: "What is the best fertilizer for maize?"
3. The chatbot will:
   - Fetch data from agricultural APIs
   - Send your question to the LLM
   - Return a response based on real agricultural data

### Step 4: Check Chat History
- Previous conversations appear in the left sidebar
- Click any session to view the full conversation
- Click the "+" button to start a new chat

## API Features

The chatbot automatically searches these resources:
- 🗺️ MASDAP WMS Capabilities
- 📊 MASDAP Datasets
- 📚 MASDAP OAI-PMH Catalog
- 🔍 MASDAP OpenSearch
- 🌍 WFP Malawi GIS Hub (DCAT-US)
- 🌍 WFP Malawi GIS Hub (DCAT-AP)

## User Features

### Authentication
- ✅ Secure signup and login
- ✅ Session-based authentication
- ✅ Automatic logout after 2 weeks of inactivity
- ✅ Protected chatbot access

### Chat Management
- ✅ Unlimited chat sessions
- ✅ Automatic session naming from first message
- ✅ Full conversation history per session
- ✅ Delete individual sessions

### User Profile
- ✅ Location information
- ✅ Specialization tracking
- ✅ Visible in sidebar for quick reference

## Keyboard Shortcuts

- **Enter** - Send message
- **Ctrl+A** - Select all in chat box
- Click user sessions - Load conversation history

## Troubleshooting

### "Session not found" error?
- Make sure you're logged in
- Try refreshing the page
- Clear browser cookies and login again

### API data not loading?
- Check your internet connection
- API calls may take 10-30 seconds
- Some endpoints may be temporarily unavailable

### Can't login?
- Verify username and password are correct
- Password is case-sensitive
- Try signing up with a new account

## Admin Access

To access Django admin panel:
```bash
# Create a superuser
python manage.py createsuperuser

# Then visit: http://localhost:8000/admin/
# Log in with superuser credentials
```

From admin, you can:
- ✅ View all users
- ✅ View chat sessions and messages
- ✅ View user profiles
- ✅ Delete users or chats
- ✅ Manage agricultural data

## Development Notes

### Modifying the Chatbot
1. Edit `chatbot/utils.py` - Change LLM behavior
2. Edit `templates/chatbot.html` - Change UI
3. Edit `chatbot/views.py` - Change backend logic

### Adding New Features
1. Update models in `chatbot/models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Update views/URLs as needed

### Environment Variables
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=your-secret-key
```

## API Response Example

**Request:**
```json
{
  "question": "What pests affect tomatoes?"
}
```

**Response:**
```json
{
  "response": "Tomatoes are commonly affected by...",
  "session_id": 1,
  "message_id": 1
}
```

## Next Chat Features to Try

1. **"How do I prevent fall armyworms?"** - Gets pest prevention
2. **"What's the best season for planting maize?"** - Seasonal advice
3. **"Which fertilizer for low-yield soils?"** - Soil management
4. **"Tell me about crop rotation benefits"** - Sustainable farming

## Performance Tips

- **First load may be slow** - APIs are being fetched
- **Subsequent chats are faster** - Only for new sessions
- **Multiple users OK** - Each has isolated sessions
- **Chat history is permanent** - Unless you delete it

## Logging Out

- Click the "Logout" button in the bottom left
- You'll be redirected to the login page
- Your chat history is saved for next login

---

**Need Help?** Check `AUTHENTICATION_SETUP.md` for detailed information.
