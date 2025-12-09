from django.db import models
from django.contrib.auth.models import User
from farmers.models import FieldVisit

class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    visit = models.ForeignKey(FieldVisit, on_delete=models.CASCADE, related_name="reports")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter.username} on {self.created_at.strftime('%Y-%m-%d')}"
