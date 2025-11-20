# Django Groups Module - AgriAssist Implementation Guide

## Overview
Django's `groups` module provides role-based access control. Groups are collections of permissions that can be assigned to users.

## Basic Concept

```
User (e.g., "john_farmer")
    ↓
    Group: "Farmers" (can view own chats, ask questions)
    Group: "Extension Officers" (can view all chats, manage resources)
    Group: "Admin" (can manage users, delete content)
```

## Step 3: Create Groups in Django Admin

1. Go to `http://localhost:8000/admin/`
2. Navigate to **Authentication and Authorization** > **Groups**
3. Click **+ Add Group**
4. Type group name: `Farmers` and click **Save**
5. Click **+ Add Group** again, type: `Extension Officers` and click **Save**
6. Repeat for: `Admins`

**That's it! You now have 3 groups. Skip the permissions section below if you're a beginner.**

## Step 2: Assign Permissions to Groups (Optional - Keep Simple!)

**For beginners, just create the groups and skip permissions.** The code doesn't use them yet anyway.

If you want to assign permissions later, keep it simple:

### Farmers Group
- (No permissions needed - they can just chat)

### Extension Officers Group
- (No permissions needed - they can manage content via admin)

### Admins Group
- (Already has all permissions as superuser)

## Step 3: Add Groups to Users

### Via Admin Panel
1. Go to **Users** > Select user
2. In "Groups" section, check desired groups
3. Save

### Programmatically in Code

```python
from django.contrib.auth.models import User, Group

# Get or create group
farmers_group, created = Group.objects.get_or_create(name='Farmers')

# Add user to group
user = User.objects.get(username='john_farmer')
user.groups.add(farmers_group)

# Remove user from group
user.groups.remove(farmers_group)

# Check if user in group
if user.groups.filter(name='Extension Officers').exists():
    print("User is an Extension Officer")
```

## Step 4: Use Groups in Views

### Check Group Membership

```python
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse

def is_extension_officer(user):
    """Check if user is in Extension Officers group"""
    return user.groups.filter(name='Extension Officers').exists()

@user_passes_test(is_extension_officer)
def manage_agricultural_data(request):
    """Only Extension Officers can access this"""
    return render(request, 'manage_data.html')
```

### Modify chatbot/views.py Example

```python
from django.contrib.auth.decorators import user_passes_test

def is_farmer(user):
    return user.groups.filter(name='Farmers').exists()

def is_officer(user):
    return user.groups.filter(name='Extension Officers').exists()

@login_required
@user_passes_test(is_farmer)
def chatbot_home(request):
    """Only Farmers can access chatbot"""
    # ... existing code
    pass

@login_required
def get_session_messages(request, session_id):
    """
    Extension Officers can view any session.
    Farmers can only view their own.
    """
    try:
        session = ChatSession.objects.get(id=session_id)
        
        # Check permissions
        is_officer = request.user.groups.filter(name='Extension Officers').exists()
        is_owner = session.user == request.user
        
        if not (is_owner or is_officer or request.user.is_staff):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # ... rest of code
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
```

## Step 5: Template-Level Access Control

```html
<!-- templates/chatbot.html -->

{% if user.groups.all|length > 0 %}
    <div class="user-role">
        {% for group in user.groups.all %}
            <span class="badge">{{ group.name }}</span>
        {% endfor %}
    </div>
{% endif %}

{% if user.groups.all|dictsort:"name"|join:"," == "Extension Officers" %}
    <!-- Show admin controls for Extension Officers -->
    <a href="/admin/chatbot/agriculturalFaq/">Manage FAQs</a>
{% endif %}
```

## Practical Example: Role-Based Chat Access

```python
# chatbot/views.py

from django.contrib.auth.models import Group

@login_required
def chatbot_api(request):
    """
    Role-based chat API
    - Farmers: Limited to 10 chats/day
    - Officers: Unlimited chats
    - Admins: Full access
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({'error': 'Question required'}, status=400)
        
        # Check user role
        is_farmer = request.user.groups.filter(name='Farmers').exists()
        is_officer = request.user.groups.filter(name='Extension Officers').exists()
        
        # Rate limiting for Farmers
        if is_farmer:
            today = timezone.now().date()
            chat_count = ChatMessage.objects.filter(
                session__user=request.user,
                created_at__date=today
            ).count()
            
            if chat_count >= 10:
                return JsonResponse({
                    'error': 'Daily chat limit (10) reached. Upgrade to Extension Officer.'
                }, status=429)
        
        # Process chat (existing code)
        # ... fetch APIs, call LLM, etc
        
        return JsonResponse({
            'response': response,
            'session_id': session.id,
            'user_role': [g.name for g in request.user.groups.all()]
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Step 6: Create Initial Groups Script

Create `chatbot/management/commands/create_groups.py`:

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from chatbot.models import ChatSession, ChatMessage, AgriculturalFAQ

class Command(BaseCommand):
    help = 'Create user groups and assign permissions'
    
    def handle(self, *args, **options):
        # Create groups
        farmers_group, _ = Group.objects.get_or_create(name='Farmers')
        officers_group, _ = Group.objects.get_or_create(name='Extension Officers')
        admins_group, _ = Group.objects.get_or_create(name='Admins')
        
        # Get content types
        session_ct = ContentType.objects.get_for_model(ChatSession)
        message_ct = ContentType.objects.get_for_model(ChatMessage)
        faq_ct = ContentType.objects.get_for_model(AgriculturalFAQ)
        
        # Farmers: View own chats
        farmers_perms = Permission.objects.filter(
            content_type__in=[session_ct, message_ct],
            codename__in=['view_chatsession', 'view_chatmessage', 'add_chatmessage']
        )
        farmers_group.permissions.set(farmers_perms)
        
        # Officers: Full chatbot + manage content
        officers_perms = Permission.objects.filter(
            content_type__in=[session_ct, message_ct, faq_ct]
        )
        officers_group.permissions.set(officers_perms)
        
        # Admins: All permissions (inherits from superuser)
        all_perms = Permission.objects.all()
        admins_group.permissions.set(all_perms)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and permissions')
        )
```

Run it:
```bash
python manage.py create_groups
```

## Use Cases for Your AgriAssist App

### 1. Rate Limiting by Role
```python
def chatbot_api(request):
    # Farmers: 5 questions/day, Officers: 50/day
    daily_limit = 50 if request.user.groups.filter(name='Extension Officers').exists() else 5
```

### 2. Content Visibility
```python
def get_sessions(request):
    # Officers see all sessions, Farmers see only theirs
    if request.user.groups.filter(name='Extension Officers').exists():
        sessions = ChatSession.objects.all()
    else:
        sessions = ChatSession.objects.filter(user=request.user)
```

### 3. Feature Access
```python
def get_context_data(request):
    context = {
        'can_export': request.user.groups.filter(name='Extension Officers').exists(),
        'can_manage_users': request.user.is_superuser,
        'can_edit_faqs': request.user.groups.filter(
            name__in=['Extension Officers', 'Admins']
        ).exists(),
    }
```

## Database Schema

```
User
  ├── groups (ManyToMany) ──→ Group
  │                             └── permissions (ManyToMany) → Permission
  │
  └── user_permissions (ManyToMany) → Permission
```

## Summary

| Task | Code |
|------|------|
| Create group | `Group.objects.create(name='Farmers')` |
| Add user to group | `user.groups.add(group)` |
| Check membership | `user.groups.filter(name='Farmers').exists()` |
| Get user groups | `user.groups.all()` |
| View permission | `user.has_perm('chatbot.view_chatsession')` |
| Add permission | `group.permissions.add(permission)` |

## Next Steps

1. Create groups via Django admin
2. Update your views to check group membership
3. Implement role-based features (rate limiting, content filtering)
4. Test with different user types

---

**Ready to implement?** I can add role-based access control to your chatbot views. Just let me know!
