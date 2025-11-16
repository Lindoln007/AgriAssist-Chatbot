# AgriAssist Chatbot

A web-based support tool for Agricultural Extension Officers in Malawi, built with Django and integrated with Mistral LLM via HuggingFace Inference API.

## Features

- **Instant Agricultural Information**: Provides quick answers to common agricultural questions (pests, fertilizers, crop care, etc.)
- **Local Database Search**: Stores and searches pre-loaded agricultural FAQs, pest information, fertilizer guidelines, crop management tips, and extension resources
- **AI-Powered Responses**: Combines local database results with Mistral LLM insights for comprehensive answers
- **Django Admin Interface**: Easy content management for extension officers
- **Simple Web Interface**: Clean, responsive chatbot UI

## Project Structure

```
AgriAssistant/
├── AgriAssistant/          # Main Django project settings
├── chatbot/               # Chatbot app
│   ├── models.py         # Database models for agricultural data
│   ├── views.py          # API endpoints and page rendering
│   ├── utils.py          # HuggingFace API integration and search logic
│   ├── admin.py          # Django admin configurations
│   ├── urls.py           # App URL routing
│   └── fixtures/         # Sample data
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS)
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
└── venv/                 # Python virtual environment
```

## Setup Instructions

1. **Clone or navigate to the project directory**

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   call venv\Scripts\activate.bat
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django requests
   ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Load sample data**
   ```bash
   python manage.py loaddata chatbot/fixtures/sample_data.json
   ```

6. **Set HuggingFace API Key**
   Set the environment variable for the HuggingFace API key:
   ```bash
   export HUGGINGFACE_API_KEY=your_api_key_here
   ```
   Or on Windows:
   ```cmd
   set HUGGINGFACE_API_KEY=your_api_key_here
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Chatbot interface: http://127.0.0.1:8000/chatbot/
   - Admin interface: http://127.0.0.1:8000/admin/

## Models

### AgriculturalFAQ
Stores frequently asked questions and answers about agriculture.

### PestInfo
Information about common agricultural pests, including symptoms, treatment, and prevention.

### FertilizerGuideline
Guidelines for fertilizer application rates, timing, and types for different crops.

### CropManagementTip
Tips for managing various crops, including spacing, watering, and seasonal advice.

### ExtensionResource
Additional resources like policies, manuals, and guides for extension officers.

## API Integration

The chatbot uses the HuggingFace Inference API with the Mistral-7B-Instruct model. Ensure you have a valid API key from HuggingFace.

## Usage

1. Navigate to the chatbot interface
2. Type your agricultural question in the input field
3. The system will search the local database and query the LLM
4. Receive a combined response with relevant information and AI insights

## Customization

- Add more sample data via Django admin or by editing fixtures
- Modify the search logic in `utils.py` for better relevance
- Customize the UI in `templates/chatbot.html`
- Adjust LLM parameters in `utils.py` for different response styles

## Requirements

- Python 3.8+
- Django 5.2+
- requests library
- HuggingFace account with API key

## Contributing

This project addresses key challenges faced by agricultural extension officers in Malawi, as outlined in reports from the National Agriculture Extension Strategy 2020–2024 and FAO studies.
