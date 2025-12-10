from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Farmer, FieldVisit
from datetime import date

def is_officer(user):
    # Depending on requirements, we can restrict this module to specific users
    # For now, we assume logged-in users (extension officers) have access
    return True

@login_required
def farmer_list(request):
    """List all farmers managed by the extension officer"""
    query = request.GET.get('q')
    farmers = Farmer.objects.filter(extension_officer=request.user)

    if query:
        farmers = farmers.filter(
            Q(name__icontains=query) |
            Q(village__icontains=query) |
            Q(main_crops__icontains=query)
        )
    
    context = {
        'farmers': farmers,
        'search_query': query,
        'current_module': 'farmers',
    }
    return render(request, 'farmers/farmer_list.html', context)

@login_required
def farmer_create(request):
    """Add a new farmer to the database"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        village = request.POST.get('village')
        farm_size = request.POST.get('farm_size')
        crops = request.POST.get('crops')
        notes = request.POST.get('notes')

        if name and village:
            Farmer.objects.create(
                name=name,
                phone_number=phone,
                village=village,
                farm_size_acres=farm_size if farm_size else None,
                main_crops=crops,
                extension_officer=request.user,
                notes=notes
            )
            messages.success(request, f'Farmer {name} added successfully!')
            return redirect('farmers:list')
        else:
            messages.error(request, 'Name and Village are required.')

    return render(request, 'farmers/farmer_form.html', {'current_module': 'farmers'})

@login_required
def farmer_detail(request, pk):
    """View farmer details and visit history"""
    farmer = get_object_or_404(Farmer, pk=pk, extension_officer=request.user)
    visits = farmer.visits.all()
    
    # Check which visits have been reported
    from reports.models import Report
    for visit in visits:
        visit.has_report = Report.objects.filter(visit=visit).exists()
    
    context = {
        'farmer': farmer,
        'visits': visits,
        'current_module': 'farmers',
    }
    return render(request, 'farmers/farmer_detail.html', context)

@login_required
def visit_create(request, farmer_id):
    """Log a new field visit"""
    farmer = get_object_or_404(Farmer, pk=farmer_id, extension_officer=request.user)
    
    if request.method == 'POST':
        visit_date = request.POST.get('visit_date')
        purpose = request.POST.get('purpose')
        observations = request.POST.get('observations')
        recommendations = request.POST.get('recommendations')
        follow_up = request.POST.get('follow_up_date')

        FieldVisit.objects.create(
            farmer=farmer,
            officer=request.user,
            visit_date=visit_date if visit_date else date.today(),
            purpose=purpose,
            observations=observations,
            recommendations=recommendations,
            follow_up_date=follow_up if follow_up else None,
            follow_up_required=bool(follow_up)
        )
        messages.success(request, 'Field visit logged successfully!')
        return redirect('farmers:detail', pk=farmer.id)

    return render(request, 'farmers/visit_form.html', {'farmer': farmer, 'current_module': 'farmers'})
