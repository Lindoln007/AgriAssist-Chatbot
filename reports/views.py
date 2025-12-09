from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from farmers.models import FieldVisit
from .models import Report

@login_required
@require_POST
def submit_report(request, visit_id):
    """
    Creates a report from a specific field visit activity log.
    Redirects back to the referring page (Farmer Detail).
    """
    visit = get_object_or_404(FieldVisit, id=visit_id)
    
    # Optional: Check if report already exists to prevent duplicates?
    # For now, we allow multiple reports for emphasis or re-reporting.
    Report.objects.create(
        reporter=request.user,
        visit=visit
    )
    
    messages.success(request, f"Report for visit on {visit.visit_date} has been sent to the admin.")
    # Redirect back to the previous page (the farmer detail view)
    return redirect(request.META.get('HTTP_REFERER', 'farmers:list'))

from django.db.models import Q

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def report_list(request):
    """
    Admin-only view: Lists all submitted reports.
    Supports filtering by reporter name or farmer name.
    Marks all unread reports as read when accessed.
    """
    # Mark all unread reports as read when the admin views the page
    Report.objects.filter(is_read=False).update(is_read=True)

    reports = Report.objects.select_related('reporter', 'visit', 'visit__farmer').all()

    query = request.GET.get('q')
    if query:
        reports = reports.filter(
            Q(reporter__username__icontains=query) |
            Q(reporter__first_name__icontains=query) |
            Q(reporter__last_name__icontains=query) |
            Q(visit__farmer__name__icontains=query)
        )

    context = {
        'reports': reports,
    }
    return render(request, 'reports/report_list.html', context)
