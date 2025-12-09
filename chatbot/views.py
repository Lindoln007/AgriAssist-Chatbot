from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .utils import query_mistral_llm, fetch_api_data, format_api_data_for_context, search_agricultural_data
from weather.utils import get_coordinates, get_weather_forecast, analyze_weather_for_farming, extract_location_from_text
from .models import ChatSession, ChatMessage, UserProfile
from reminders.models import FarmReminder
from datetime import date

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
            display_name = data.get('display_name', '').strip() or None

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
                display_name=display_name,
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

def login_selection(request):
    """
    Landing page to select between User and Admin login.
    """
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        return redirect('chatbot:home')
    return render(request, 'login_selection.html')

def user_login(request):
    """
    User signin view.
    Allows both regular users and admins to log in and access the chatbot.
    Admins retain their privileges when logging in through this portal.
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
                # Allow both regular users and admins to log in
                # Admins will retain their privileges (is_staff, is_superuser)
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful!', 'redirect_url': reverse('chatbot:home')})
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    context = {
        'submit_url': reverse('chatbot:user_login'),
        'page_title': 'User Sign In - AgriAssist',
        'header_title': 'AgriAssist',
        'welcome_text': 'Welcome back! Please sign in to continue.',
        'show_signup_link': True
    }
    return render(request, 'login.html', context)

def admin_login(request):
    """
    Admin signin view.
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
                # Strictly authenticate only admins
                if not (user.is_staff or user.is_superuser):
                    return JsonResponse({'error': 'You do not have admin privileges.'}, status=403)
                
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful!', 'redirect_url': '/admin/'})
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    context = {
        'submit_url': reverse('chatbot:admin_login'),
        'page_title': 'Admin Sign In - AgriAssist',
        'header_title': 'Admin Portal',
        'welcome_text': 'Please sign in to access the admin dashboard.',
        'show_signup_link': False
    }
    return render(request, 'login.html', context)

@login_required
def signout(request):
    """
    User signout view.
    """
    logout(request)
    return redirect('chatbot:login_selection')

@login_required
def chatbot_home(request):
    """
    Renders the chatbot interface.
    Only accessible to logged-in users.
    """
    # Ensure a UserProfile exists for the logged-in user (superusers created via
    # createsuperuser may not have a profile). This prevents RelatedObjectDoesNotExist
    # exceptions when templates or code expect `user.profile`.
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Keep sessions strictly scoped to the authenticated user. If the user is an
    # admin, mark that in the context so templates can treat admin accounts
    # differently if desired — but do not merge admin data with regular users.
    chat_sessions = ChatSession.objects.filter(user=request.user)

    # Count unread government updates
    from policy_updates.models import GovUpdate, UserUpdateView
    all_updates = GovUpdate.objects.all()
    viewed_update_ids = UserUpdateView.objects.filter(user=request.user).values_list('update_id', flat=True)
    unread_updates_count = all_updates.exclude(id__in=viewed_update_ids).count()

    context = {
        'user_profile': user_profile,
        'chat_sessions': chat_sessions,
        'is_admin': request.user.is_staff or request.user.is_superuser,
        'due_today_count': FarmReminder.objects.filter(user=request.user, date=date.today(), status='pending').count(),
        'unread_updates_count': unread_updates_count,
        'unread_reports_count': 0,
    }

    # Add unread report count for admins
    if request.user.is_staff or request.user.is_superuser:
        from reports.models import Report
        # Assuming 'is_read' field exists, otherwise we treat all as new for now or add the field
        # The Report model created earlier has 'is_read' defaulting to False
        context['unread_reports_count'] = Report.objects.filter(is_read=False).count()
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

        # Get or create chat session. Enforce strict ownership: only the session
        # owner (or admin for viewing) can use a session. Regular users cannot use
        # sessions they don't own; a new session is created for them instead.
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                # See if session exists but belongs to someone else
                other = ChatSession.objects.filter(id=session_id).first()
                if other and (request.user.is_staff or request.user.is_superuser):
                    # Admin can view/use other users' sessions for admin workflows
                    session = other
                else:
                    # Regular users must have their own session; create a new one
                    session = ChatSession.objects.create(user=request.user)
        if not session:
            session = ChatSession.objects.create(user=request.user)

        # If the question matches a local FAQ or other DB content, prefer the
        # stored answer so users get the pre-installed authoritative response.
        faq_results = []
        try:
            faq_results = search_agricultural_data(question)
        except Exception:
            faq_results = []

        if faq_results:
            # Use the first matching result as the authoritative answer.
            faq_answer = faq_results[0]

            message = ChatMessage.objects.create(
                session=session,
                user_message=question,
                bot_response=faq_answer,
            )

            # Update session title only if no title is set (first message)
            if not session.title:
                session.title = question[:100]
                session.save()

            return JsonResponse({
                'response': faq_answer,
                'session_id': session.id,
                'message_id': message.id,
                'source': 'faq',
            })

        # Fetch data from agricultural APIs
        api_data = fetch_api_data()
        api_context = format_api_data_for_context(api_data)

        # --- Weather Integration ---
        # Check if weather is relevant to the question
        weather_keywords = ['weather', 'rain', 'temperature', 'forecast', 'plant', 'irrigation', 'farm', 'crop', 'pest', 'disease']
        if any(keyword in question.lower() for keyword in weather_keywords):
            # 1. Try to find location in the question
            target_location = extract_location_from_text(question)
            
            # 2. If not found, prefer any temporary session override, then user's profile location
            if not target_location:
                # session-based temporary override (set by weather page searches)
                session_override = None
                try:
                    session_override = request.session.get('weather_override')
                except Exception:
                    session_override = None

                if session_override:
                    target_location = session_override
                else:
                    try:
                        user_profile = UserProfile.objects.get(user=request.user)
                        if user_profile.location:
                            target_location = user_profile.location
                    except UserProfile.DoesNotExist:
                        pass
            
            # 3. Default to Lilongwe if still unknown
            if not target_location:
                target_location = "Lilongwe"

            # Fetch weather data
            coords = get_coordinates(target_location)
            if coords:
                w_data = get_weather_forecast(coords['lat'], coords['lon'])
                if w_data:
                    analysis = analyze_weather_for_farming(w_data)
                    weather_context = f"\n\n### 🌤️ Real-time Weather for {coords['name']} (Malawi):\n"
                    weather_context += f"- **Temperature:** {w_data['current_weather']['temperature']}°C\n"
                    weather_context += f"- **Wind Speed:** {w_data['current_weather']['windspeed']} km/h\n"
                    weather_context += f"- **Wind Direction:** {w_data['current_weather']['winddirection']}°\n"
                    weather_context += f"- **Farming Analysis:** {analysis}\n"
                    
                    api_context += weather_context
        # ---------------------------

        # Build conversation history from previous messages in this session
        # and pass it to the LLM so it can maintain conversational state.
        conversation_history = []
        try:
            # Only include a recent slice to avoid overly long prompts
            recent_msgs = session.messages.order_by('created_at').all()
            # keep last 10 message pairs (user+bot)
            if recent_msgs.exists():
                # Convert to list and take the last N
                msgs_list = list(recent_msgs)[-10:]
                for msg in msgs_list:
                    conversation_history.append({
                        'user_message': msg.user_message,
                        'bot_response': msg.bot_response,
                    })
        except Exception:
            conversation_history = []

        # Determine which user name should be presented to the LLM. Use the
        # session owner (session.user) rather than the currently logged-in user
        # so admins viewing sessions do not cause the bot to address the admin.
        try:
            owner = session.user
        except Exception:
            owner = request.user

        # Prefer the UserProfile.display_name if set, then the user's full name,
        # then fall back to the username so the bot uses the preferred name.
        owner_display_name = None
        try:
            owner_profile, _ = UserProfile.objects.get_or_create(user=owner)
            owner_display_name = owner_profile.display_name
        except Exception:
            pass
        if not owner_display_name:
            owner_display_name = owner.get_full_name()
        if not owner_display_name:
            owner_display_name = owner.username

        # Query LLM with API context, the session owner's display name and
        # conversation history so replies address the correct person.
        response = query_mistral_llm(
            question,
            api_context,
            username=owner_display_name,
            conversation=conversation_history,
        )

        # Store message in database
        message = ChatMessage.objects.create(
            session=session,
            user_message=question,
            bot_response=response
        )

        # Update session title only if no title is set (first message)
        if not session.title:
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
        # Enforce strict ownership: only the session owner (or admin) can view.
        # If regular user requests a session they don't own, return 404.
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            other = ChatSession.objects.filter(id=session_id).first()
            if other and (request.user.is_staff or request.user.is_superuser):
                # Admin can view other users' sessions
                session = other
            else:
                # Regular users cannot access sessions they don't own
                return JsonResponse({'error': 'Chat session not found.'}, status=404)

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
