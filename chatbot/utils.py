import os
from groq import Groq
from django.conf import settings
from django.db import models
from dotenv import load_dotenv

load_dotenv()

def query_mistral_llm(question):
    """
    Queries the Groq LLM API using Llama 3.1 8B model.
    Requires GROQ_API_KEY environment variable.
    """
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return "Error: Groq API key not set. Please set GROQ_API_KEY environment variable."

    client = Groq(api_key=api_key)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are AgriAssist an agriculture extension assistant chatbot , developed by Asante Mbaya "
                        "Provide accurate, verified, and Malawi-relevant farming information. "
                        "Explain concepts simply, avoid hallucinations, and only answer non-agricultural "
                        "questions if absolutely necessary."
                    )
                },
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error querying LLM: {str(e)}"


def search_agricultural_data(question):
    """
    Searches the local database for relevant agricultural information.
    Simple keyword search. For production, use full-text search.
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

    # Search FAQs
    faqs = AgriculturalFAQ.objects.filter(
        models.Q(question__icontains=keywords[0]) |
        models.Q(answer__icontains=keywords[0])
    )
    for faq in faqs:
        results.append(faq.answer)

    # Search Pest Info
    pests = PestInfo.objects.filter(
        models.Q(name__icontains=keywords[0]) |
        models.Q(description__icontains=keywords[0])
    )
    for pest in pests:
        results.append(f"{pest.name}: {pest.symptoms}. Treatment: {pest.treatment}")

    # Search Fertilizer Guidelines
    fertilizers = FertilizerGuideline.objects.filter(
        models.Q(crop_type__icontains=keywords[0]) |
        models.Q(fertilizer_type__icontains=keywords[0])
    )
    for fert in fertilizers:
        results.append(
            f"For {fert.crop_type}: Use {fert.fertilizer_type} at {fert.application_rate}"
        )

    # Search Crop Tips
    tips = CropManagementTip.objects.filter(
        models.Q(crop_type__icontains=keywords[0]) |
        models.Q(tip_content__icontains=keywords[0])
    )
    for tip in tips:
        results.append(f"{tip.tip_title}: {tip.tip_content}")

    # Search Extension Resources
    resources = ExtensionResource.objects.filter(
        models.Q(title__icontains=keywords[0]) |
        models.Q(content__icontains=keywords[0])
    )
    for res in resources:
        results.append(f"{res.title}: {res.content[:200]}...")

    return results[:5]  # still safe, you can change to [:1] if needed
