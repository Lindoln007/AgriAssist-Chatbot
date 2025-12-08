from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from .models import GovUpdate
from .forms import GovUpdateForm

def is_staff(user):
    return user.is_staff

# Admin Views (CRUD)
@login_required
@user_passes_test(is_staff)
def admin_list(request):
    """Admin page to list all government updates"""
    updates = GovUpdate.objects.all()
    context = {
        'updates': updates,
    }
    return render(request, 'policy_updates/admin_list.html', context)

@login_required
@user_passes_test(is_staff)
def admin_create(request):
    """Admin page to create a new government update"""
    if request.method == 'POST':
        form = GovUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.created_by = request.user
            update.save()
            messages.success(request, 'Government update created successfully!')
            return redirect('policy_updates:admin_list')
    else:
        form = GovUpdateForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'policy_updates/admin_form.html', context)

@login_required
@user_passes_test(is_staff)
def admin_edit(request, pk):
    """Admin page to edit an existing government update"""
    update = get_object_or_404(GovUpdate, pk=pk)
    
    if request.method == 'POST':
        form = GovUpdateForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Government update updated successfully!')
            return redirect('policy_updates:admin_list')
    else:
        form = GovUpdateForm(instance=update)
    
    context = {
        'form': form,
        'update': update,
        'action': 'Edit',
    }
    return render(request, 'policy_updates/admin_form.html', context)

@login_required
@user_passes_test(is_staff)
def admin_delete(request, pk):
    """Admin page to delete a government update"""
    update = get_object_or_404(GovUpdate, pk=pk)
    
    if request.method == 'POST':
        update.delete()
        messages.success(request, 'Government update deleted successfully!')
        return redirect('policy_updates:admin_list')
    
    context = {
        'update': update,
    }
    return render(request, 'policy_updates/admin_delete.html', context)

# User Views (Read-only)
@login_required
def user_list(request):
    """User-facing page to view all government updates"""
    from .models import UserUpdateView
    
    updates = GovUpdate.objects.all()
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        updates = updates.filter(category=category)
    
    # Search by keyword
    search = request.GET.get('search')
    if search:
        updates = updates.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search)
        )
    
    # Get viewed update IDs for this user
    viewed_update_ids = set(UserUpdateView.objects.filter(user=request.user).values_list('update_id', flat=True))
    
    # Annotate each update with whether it's been viewed by this user
    for update in updates:
        update.is_new = update.id not in viewed_update_ids
    
    # Get all categories for filter dropdown
    categories = GovUpdate.CATEGORY_CHOICES
    
    context = {
        'updates': updates,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
    }
    return render(request, 'policy_updates/user_list.html', context)

@login_required
def user_detail(request, pk):
    """User-facing page to view full details of a government update"""
    from .models import UserUpdateView
    
    update = get_object_or_404(GovUpdate, pk=pk)
    
    # Mark this update as viewed by this user
    UserUpdateView.objects.get_or_create(user=request.user, update=update)
    
    # Update is no longer new since user is viewing it
    update.is_new = False
    
    context = {
        'update': update,
        'is_new': False,  # Never show as new in detail view since user is viewing it
    }
    return render(request, 'policy_updates/user_detail.html', context)

@login_required
def dashboard_feed(request):
    """Get latest 3 updates for dashboard feed"""
    from .models import UserUpdateView
    
    updates = GovUpdate.objects.all()[:3]
    
    # Get viewed update IDs for this user
    viewed_update_ids = set(UserUpdateView.objects.filter(user=request.user).values_list('update_id', flat=True))
    
    # Mark updates as new if user hasn't viewed them
    for update in updates:
        update.is_new = update.id not in viewed_update_ids
    
    return updates
