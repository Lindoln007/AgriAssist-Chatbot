from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .utils import query_mistral_llm, fetch_api_data, format_api_data_for_context
from .models import ChatSession, ChatMessage, UserProfile

def signup(request):
    """
    User signup view.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            location = data.get('location', '').strip()
            specialization = data.get('specialization', '').strip()

            # Validation
            if not username or not email or not password:
                return JsonResponse({'error': 'Username, email, and password are required.'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists.'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists.'}, status=400)

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                location=location,
                specialization=specialization
            )

            # Log the user in
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Account created successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return render(request, 'signup.html')

def signin(request):
    """
    User signin view.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required.'}, status=400)

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful!'})
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return render(request, 'login.html')

@login_required
def signout(request):
    """
    User signout view.
    """
    logout(request)
    return redirect('chatbot:login')

@login_required
def chatbot_home(request):
    """
    Renders the chatbot interface.
    Only accessible to logged-in users.
    """
    user_profile = request.user.profile
    chat_sessions = ChatSession.objects.filter(user=request.user)
    
    context = {
        'user_profile': user_profile,
        'chat_sessions': chat_sessions,
    }
    return render(request, 'chatbot.html', context)

@login_required
@require_POST
def chatbot_api(request):
    """
    API endpoint for chatbot queries.
    Expects POST request with JSON body containing 'question' and optional 'session_id'.
    Stores conversation in database and fetches API data for context.
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        session_id = data.get('session_id')

        if not question:
            return JsonResponse({'error': 'Question is required.'}, status=400)

        # Get or create chat session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return JsonResponse({'error': 'Chat session not found.'}, status=404)
        else:
            session = ChatSession.objects.create(user=request.user)

        # Fetch data from agricultural APIs
        api_data = fetch_api_data()
        api_context = format_api_data_for_context(api_data)

        # Query LLM with API context and user's name
        response = query_mistral_llm(question, api_context, username=request.user.username)

        # Store message in database
        message = ChatMessage.objects.create(
            session=session,
            user_message=question,
            bot_response=response
        )

        # Update session title if it's the first message
        if session.messages.count() == 1:
            session.title = question[:100]
            session.save()

        return JsonResponse({
            'response': response,
            'session_id': session.id,
            'message_id': message.id,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@login_required
def get_session_messages(request, session_id):
    """
    Retrieves all messages from a specific chat session.
    """
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        messages = session.messages.all()
        
        message_list = [
            {
                'id': msg.id,
                'user_message': msg.user_message,
                'bot_response': msg.bot_response,
                'created_at': msg.created_at.isoformat(),
            }
            for msg in messages
        ]
        
        return JsonResponse({
            'session_id': session.id,
            'title': session.title,
            'created_at': session.created_at.isoformat(),
            'messages': message_list,
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Chat session not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@login_required
def delete_session(request, session_id):
    """
    Deletes a chat session.
    """
    if request.method == 'POST':
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
            return JsonResponse({'success': True, 'message': 'Session deleted successfully.'})
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Chat session not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed.'}, status=405)

@login_required
def get_user_sessions(request):
    """
    Returns all chat sessions for the current user (for sidebar).
    """
    try:
        sessions = ChatSession.objects.filter(user=request.user).values('id', 'title', 'created_at')
        sessions_list = [
            {
                'id': session['id'],
                'title': session['title'] or 'Untitled Chat',
                'created_at': session['created_at'].isoformat(),
            }
            for session in sessions
        ]
        return JsonResponse({'sessions': sessions_list})
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

