from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class Conversation(models.Model):
    """Stores chat conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title[:50]}"
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    """Stores individual messages in a conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['created_at']

class UserPreference(models.Model):
    """Stores manager preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_preferences')
    
    # Report Preferences
    preferred_report_frequency = models.CharField(max_length=50, default='daily')
    preferred_report_format = models.CharField(max_length=50, default='summary')
    
    # Inventory Alert Thresholds
    low_stock_threshold = models.IntegerField(default=10)
    
    # Frequently Monitored Products (JSON array)
    monitored_products = models.JSONField(default=list)
    
    # Business Rules (JSON object)
    business_rules = models.JSONField(default=dict)
    
    # Last interaction
    last_interaction = models.DateTimeField(null=True, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        preference, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'low_stock_threshold': 10,
                'monitored_products': [],
                'business_rules': {}
            }
        )
        return preference

class BusinessInsight(models.Model):
    """Stores AI-generated business insights"""
    INSIGHT_TYPES = [
        ('sales', 'Sales Insight'),
        ('inventory', 'Inventory Insight'),
        ('user', 'User Insight'),
        ('recommendation', 'Recommendation'),
        ('alert', 'Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class AgentActionLog(models.Model):
    """Logs AI agent actions for auditing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_logs')
    agent_name = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    duration_ms = models.FloatField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.agent_name} - {self.action} - {self.created_at}"
