from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extended user profile for tracking agricultural extension officers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class ChatSession(models.Model):
    """Stores chat sessions and conversations for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

class ChatMessage(models.Model):
    """Individual messages within a chat session"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message in {self.session}"

class AgriculturalFAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'pests', 'fertilizers', 'crop_care'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class PestInfo(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    symptoms = models.TextField()
    treatment = models.TextField()
    prevention = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'insects', 'fungi'

    def __str__(self):
        return self.name

class FertilizerGuideline(models.Model):
    crop_type = models.CharField(max_length=200)
    fertilizer_type = models.CharField(max_length=200)
    application_rate = models.CharField(max_length=200)
    timing = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.crop_type} - {self.fertilizer_type}"

class CropManagementTip(models.Model):
    crop_type = models.CharField(max_length=200)
    tip_title = models.CharField(max_length=300)
    tip_content = models.TextField()
    season = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'rainy', 'dry'

    def __str__(self):
        return self.tip_title

class ExtensionResource(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    resource_type = models.CharField(max_length=100, choices=[
        ('guide', 'Guide'),
        ('manual', 'Manual'),
        ('policy', 'Policy'),
        ('other', 'Other')
    ], default='guide')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
