import os
from groq import Groq
from django.conf import settings
from django.db import models
from dotenv import load_dotenv
import requests
import json
from xml.etree import ElementTree as ET
from typing import List, Dict

load_dotenv()

# API Endpoints for agricultural data
API_ENDPOINTS = [
    "https://www.masdap.mw/geoserver/ows?service=WMS&version=1.1.1&request=GetCapabilities",
    "https://www.masdap.mw/api/datasets/",
    "https://www.masdap.mw/catalogue/csw?mode=oaipmh&verb=Identify",
    "https://www.masdap.mw/catalogue/csw?mode=opensearch&service=CSW&version=2.0.2&request=GetCapabilities",
    "https://wfp-malawi-gis-hub-unwfp.hub.arcgis.com/api/feed/dcat-us/1.1.json",
    "https://wfp-malawi-gis-hub-unwfp.hub.arcgis.com/api/feed/dcat-ap/2.0.1.json",
]

def fetch_api_data(timeout: int = None) -> Dict[str, any]:
    """
    Fetches data from all agricultural data API endpoints.
    Returns a dictionary with endpoint URLs as keys and their data/status as values.
    """
    if timeout is None:
        timeout = getattr(settings, 'API_TIMEOUT', 30)
    
    api_data = {}
    
    for endpoint in API_ENDPOINTS:
        try:
            response = requests.get(endpoint, timeout=timeout)
            response.raise_for_status()
            
            # Parse based on content type
            if 'application/json' in response.headers.get('content-type', ''):
                api_data[endpoint] = {
                    'status': 'success',
                    'data': response.json(),
                }
            elif 'application/xml' in response.headers.get('content-type', '') or 'text/xml' in response.headers.get('content-type', ''):
                api_data[endpoint] = {
                    'status': 'success',
                    'data': response.text[:1000],  # Limit XML to 1000 chars
                }
            else:
                api_data[endpoint] = {
                    'status': 'success',
                    'data': response.text[:500],  # Limit text to 500 chars
                }
        except requests.exceptions.Timeout:
            api_data[endpoint] = {
                'status': 'error',
                'error': 'Request timeout',
            }
        except requests.exceptions.ConnectionError:
            api_data[endpoint] = {
                'status': 'error',
                'error': 'Connection error',
            }
        except Exception as e:
            api_data[endpoint] = {
                'status': 'error',
                'error': str(e),
            }
    
    return api_data

def format_api_data_for_context(api_data: Dict[str, any]) -> str:
    """
    Formats the fetched API data into a string for LLM context.
    """
    context = "### Available Agricultural Data Sources:\n\n"
    
    for endpoint, data in api_data.items():
        context += f"**Source:** {endpoint}\n"
        if data['status'] == 'success':
            if isinstance(data['data'], dict):
                # JSON data
                summary = json.dumps(data['data'], indent=2)[:500]
            else:
                # Text/XML data
                summary = data['data']
            context += f"**Data:** {summary}\n"
        else:
            context += f"**Status:** Error - {data.get('error', 'Unknown error')}\n"
        context += "\n"
    
    return context

def query_mistral_llm(question: str, api_context: str = "", username: str = None, conversation: List[Dict[str, str]] = None) -> str:
    """
    Queries the Groq LLM API using Llama 3.1 8B model.
    Includes context from agricultural data APIs.
    Includes user context if username provided.
    Requires GROQ_API_KEY environment variable.
    """
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return "Error: Groq API key not set. Please set GROQ_API_KEY environment variable."

    client = Groq(api_key=api_key)

    try:
        user_context = f"The user's name is {username}. " if username else ""
        system_message = (
            "You are AgriAssist, an agriculture extension assistant chatbot, developed by Asante Mbaya. "
            f"{user_context}"
            "Provide accurate, verified, and Malawi-relevant farming information. "
            "Explain concepts simply, avoid hallucinations, and only answer non-agricultural "
            "questions if absolutely necessary. "
            "Use the provided agricultural data sources to enhance your responses when relevant."
        )
        
        if api_context:
            system_message += f"\n\n{api_context}"

        # Build the message list for the chat completion. Start with system message.
        messages = [
            {"role": "system", "content": system_message}
        ]

        # If conversation history is provided, append prior user/assistant turns.
        # `conversation` is expected to be a list of dicts with keys like
        # {'user_message': '...', 'bot_response': '...'} or already in
        # {'role': 'user'|'assistant', 'content': '...'} form.
        if conversation:
            for entry in conversation:
                # If entry already looks like a chat message dict, use it.
                if 'role' in entry and 'content' in entry:
                    messages.append({'role': entry['role'], 'content': entry['content']})
                    continue

                # Otherwise, expect user_message and bot_response fields.
                user_msg = entry.get('user_message')
                bot_msg = entry.get('bot_response')
                if user_msg:
                    messages.append({'role': 'user', 'content': user_msg})
                if bot_msg:
                    messages.append({'role': 'assistant', 'content': bot_msg})

        # Append the current user question as the latest user message.
        messages.append({'role': 'user', 'content': question})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error querying LLM: {str(e)}"


def search_agricultural_data(question: str) -> List[str]:
    """
    Searches the local database for relevant agricultural information.
    Searches all keywords in the question, not just the first one.
    For production, use full-text search or embeddings-based retrieval.
    """
    from .models import (
        AgriculturalFAQ,
        PestInfo,
        FertilizerGuideline,
        CropManagementTip,
        ExtensionResource,
    )

    keywords = question.lower().split()
    results = []

    if not keywords:
        return results

    # Build query to match any keyword in question or answer
    query = models.Q()
    for keyword in keywords:
        query |= models.Q(question__icontains=keyword) | models.Q(answer__icontains=keyword)

    # Search FAQs with all keywords, not just the first
    faqs = AgriculturalFAQ.objects.filter(query)
    for faq in faqs:
        results.append(faq.answer)

    # Search Pest Info with all keywords
    pests = PestInfo.objects.filter(query)
    for pest in pests:
        results.append(f"{pest.name}: {pest.symptoms}. Treatment: {pest.treatment}")

    # Search Fertilizer Guidelines with all keywords
    fertilizer_query = models.Q()
    for keyword in keywords:
        fertilizer_query |= models.Q(crop_type__icontains=keyword) | models.Q(fertilizer_type__icontains=keyword)
    fertilizers = FertilizerGuideline.objects.filter(fertilizer_query)
    for fert in fertilizers:
        results.append(
            f"For {fert.crop_type}: Use {fert.fertilizer_type} at {fert.application_rate}"
        )

    # Search Crop Tips with all keywords
    tip_query = models.Q()
    for keyword in keywords:
        tip_query |= models.Q(crop_type__icontains=keyword) | models.Q(tip_content__icontains=keyword)
    tips = CropManagementTip.objects.filter(tip_query)
    for tip in tips:
        results.append(f"{tip.tip_title}: {tip.tip_content}")

    # Search Extension Resources with all keywords
    resource_query = models.Q()
    for keyword in keywords:
        resource_query |= models.Q(title__icontains=keyword) | models.Q(content__icontains=keyword)
    resources = ExtensionResource.objects.filter(resource_query)
    for res in resources:
        results.append(f"{res.title}: {res.content[:200]}...")

    return results[:5]

