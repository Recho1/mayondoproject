from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/conversations/', views.get_conversations, name='conversations'),
    path('api/conversations/<int:conversation_id>/messages/', views.get_conversation_messages, name='messages'),
    path('api/conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete'),
    path('api/insights/', views.get_insights, name='insights'),
    path('api/preferences/', views.get_preferences, name='preferences'),
    path('api/preferences/update/', views.update_preferences, name='update_preferences'),
]
