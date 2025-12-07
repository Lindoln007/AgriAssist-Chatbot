from django.db import models
from django.contrib.auth.models import User
from datetime import time

class FarmReminder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    activity_type = models.CharField(max_length=100)
    crop_or_livestock = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField(default=time(8, 0))  # Default to 8:00 AM
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_type} - {self.crop_or_livestock} ({self.date} at {self.time.strftime('%H:%M')})"

    class Meta:
        ordering = ['date', 'time']
