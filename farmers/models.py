from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Farmer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    village = models.CharField(max_length=100, help_text="Village or Location Name")
    farm_size_acres = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Size of farm in acres")
    main_crops = models.CharField(max_length=200, help_text="Comma-separated list of main crops grown")
    extension_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="managed_farmers")
    joined_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class FieldVisit(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="visits")
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    visit_date = models.DateField(default=timezone.now)
    purpose = models.CharField(max_length=200, help_text="Reason for visit (e.g., Pest Check, Routine, Harvest)")
    observations = models.TextField(help_text="Key observations made during the visit")
    recommendations = models.TextField(blank=True, help_text="Advice given to the farmer")
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"Visit to {self.farmer.name} on {self.visit_date}"
