from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import query_mistral_llm

def chatbot_home(request):
    """
    Renders the chatbot interface.
    """
    return render(request, 'chatbot.html')

@csrf_exempt
def chatbot_api(request):
    """
    API endpoint for chatbot queries.
    Expects POST request with JSON body containing 'question'.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            if not question:
                return JsonResponse({'error': 'Question is required.'}, status=400)

            response = query_mistral_llm(question)
            return JsonResponse({'response': response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method allowed.'}, status=405)
