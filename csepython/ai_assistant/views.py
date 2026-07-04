from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
from .models import Conversation, Message, UserPreference, BusinessInsight
from .agents import AgentOrchestrator
from .tools import BusinessTools

logger = logging.getLogger(__name__)

@login_required
def chat_view(request):
    """Render the chat interface"""
    if not is_manager(request.user):
        return redirect('/sales/')
    
    conversations = Conversation.objects.filter(user=request.user)
    
    context = {
        'conversations': conversations,
        'user': request.user
    }
    return render(request, 'ai_assistant/chat.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint for chat"""
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        query = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not query:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Process query using agent
        agent = AgentOrchestrator(user=request.user)
        result = agent.process_query(query, conversation_id)
        
        return JsonResponse({
            'response': result['response'],
            'conversation_id': conversation_id,
            'agent_used': result['agent_used']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_conversations(request):
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    conversations = Conversation.objects.filter(user=request.user)
    data = [{
        'id': c.id,
        'title': c.title,
        'updated_at': c.updated_at.isoformat(),
        'message_count': c.messages.count()
    } for c in conversations]
    
    return JsonResponse({'conversations': data})

@login_required
def get_conversation_messages(request, conversation_id):
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    conversation = Conversation.objects.get(id=conversation_id, user=request.user)
    messages = conversation.messages.all()
    
    data = [{
        'id': m.id,
        'role': m.role,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages]
    
    return JsonResponse({'messages': data})

@login_required
def delete_conversation(request, conversation_id):
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    conversation = Conversation.objects.get(id=conversation_id, user=request.user)
    conversation.delete()
    
    return JsonResponse({'success': True})

@login_required
def get_insights(request):
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    tools = BusinessTools(user=request.user)
    insights = tools.generate_insights()
    
    for insight in insights:
        BusinessInsight.objects.create(
            user=request.user,
            insight_type=insight['type'],
            title=insight['title'],
            description=insight['description'],
            data=insight['data']
        )
    
    return JsonResponse({'insights': insights})

@login_required
def get_preferences(request):
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        'preferred_report_frequency': preferences.preferred_report_frequency,
        'preferred_report_format': preferences.preferred_report_format,
        'low_stock_threshold': preferences.low_stock_threshold,
        'monitored_products': preferences.monitored_products,
        'email_notifications': preferences.email_notifications
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_preferences(request):
    if not is_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        preferences, _ = UserPreference.objects.get_or_create(user=request.user)
        
        if 'preferred_report_frequency' in data:
            preferences.preferred_report_frequency = data['preferred_report_frequency']
        if 'preferred_report_format' in data:
            preferences.preferred_report_format = data['preferred_report_format']
        if 'low_stock_threshold' in data:
            preferences.low_stock_threshold = data['low_stock_threshold']
        if 'monitored_products' in data:
            preferences.monitored_products = data['monitored_products']
        if 'email_notifications' in data:
            preferences.email_notifications = data['email_notifications']
        
        preferences.save()
        
        return JsonResponse({'success': True, 'preferences': {
            'preferred_report_frequency': preferences.preferred_report_frequency,
            'preferred_report_format': preferences.preferred_report_format,
            'low_stock_threshold': preferences.low_stock_threshold,
            'monitored_products': preferences.monitored_products,
            'email_notifications': preferences.email_notifications
        }})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def is_manager(user):
    try:
        return user.profile.role == 'manager'
    except:
        return False
