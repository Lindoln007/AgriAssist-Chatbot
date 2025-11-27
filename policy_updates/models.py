from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class GovUpdate(models.Model):
    CATEGORY_CHOICES = [
        ('subsidy', 'Subsidy'),
        ('policy', 'Policy'),
        ('regulation', 'Regulation'),
        ('grant', 'Grant'),
        ('training', 'Training Program'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content = models.TextField()
    file = models.FileField(
        upload_to='policy_updates/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Optional PDF file (max 10MB)'
    )
    date_posted = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gov_updates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_posted', '-created_at']
        verbose_name = 'Government Update'
        verbose_name_plural = 'Government Updates'
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
