from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import FarmReminder
from datetime import date

@login_required
def index(request):
    """Main reminders page: list + calendar + add form"""
    reminders = FarmReminder.objects.filter(user=request.user)
    today = date.today()
    due_today_count = reminders.filter(date=today, status='pending').count()
    
    context = {
        'reminders': reminders,
        'due_today_count': due_today_count,
    }
    return render(request, 'reminders/index.html', context)

@login_required
@require_POST
def add_reminder(request):
    """Handle adding a new reminder"""
    activity_type = request.POST.get('activity_type')
    crop_or_livestock = request.POST.get('crop_or_livestock')
    reminder_date = request.POST.get('date')
    reminder_time = request.POST.get('time')
    notes = request.POST.get('notes')

    if activity_type and crop_or_livestock and reminder_date and reminder_time:
        FarmReminder.objects.create(
            user=request.user,
            activity_type=activity_type,
            crop_or_livestock=crop_or_livestock,
            date=reminder_date,
            time=reminder_time,
            notes=notes
        )
    
    return redirect('reminders:index')

@login_required
@require_POST
def update_status(request, reminder_id):
    """Toggle status or set to specific status"""
    reminder = get_object_or_404(FarmReminder, id=reminder_id, user=request.user)
    new_status = request.POST.get('status')
    
    if new_status in ['pending', 'completed']:
        reminder.status = new_status
        reminder.save()
        
    return redirect('reminders:index')

@login_required
def api_events(request):
    """Return reminders as JSON for FullCalendar"""
    reminders = FarmReminder.objects.filter(user=request.user)
    events = []
    
    for r in reminders:
        color = '#2F855A' if r.status == 'completed' else '#F6E05E' # Green if done, Yellow if pending
        if r.status == 'pending' and r.date < date.today():
            color = '#E53E3E' # Red if overdue
            
        events.append({
            'id': r.id,
            'title': f"{r.activity_type} - {r.crop_or_livestock} ({r.time.strftime('%I:%M %p')})",
            'start': r.date.isoformat(),
            'description': r.notes,
            'status': r.status,
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'activity': r.activity_type,
                'crop': r.crop_or_livestock,
                'time': r.time.strftime('%I:%M %p'),
                'notes': r.notes,
                'status': r.status
            }
        })
        
    return JsonResponse(events, safe=False)
