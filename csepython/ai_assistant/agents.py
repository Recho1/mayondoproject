import json
import logging
from typing import Dict, Any
from django.utils import timezone
from .tools import BusinessTools

logger = logging.getLogger(__name__)

GREETINGS = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'sup', 'yo']

SUMMARY_TRIGGERS = [
    'summary', 'overview', 'how is business', "how's business", 'business doing',
    'business performance', 'give me a report', 'full report', 'everything', 'all data'
]

SALES_TRIGGERS = ['sale', 'sold', 'revenue', 'sell', 'order', 'today', 'daily', 'weekly', 'monthly', 'top', 'best', 'popular']
INVENTORY_TRIGGERS = ['stock', 'inventory', 'product', 'restock', 'supplier', 'warehouse']
USER_TRIGGERS = ['user', 'employee', 'staff', 'role', 'permission']

NO_MARKDOWN_INSTRUCTION = (
    "Write in plain conversational text only. "
    "Do not use markdown syntax of any kind: no asterisks, no bold, no headings, no # symbols, "
    "no emoji or icons. If you need a list, use a plain hyphen '-' at the start of a line. "
    "Keep it clean, professional, and easy to read as plain text."
)


class AgentOrchestrator:
    """
    Production-ready AI Assistant for Mayondo Wood and Furniture System.
    Uses direct OpenAI-compatible API calls (Groq by default, OpenAI as fallback).
    """

    def __init__(self, user=None):
        self.user = user
        self.tools = BusinessTools(user=user)
        self.conversation_history = []

    def process_query(self, query: str, conversation_id: int = None) -> Dict[str, Any]:
        """Process a user query and return a response"""

        if conversation_id:
            from .models import Conversation
            try:
                conv = Conversation.objects.get(id=conversation_id, user=self.user)
                history = [
                    {'role': msg.role, 'content': msg.content}
                    for msg in conv.messages.all()[:20]
                ]
                self.conversation_history = history
            except Exception as e:
                logger.warning(f"Could not load conversation history for id={conversation_id}: {e}")
                self.conversation_history = []

        query_lower = query.lower().strip()
        data = {}

        is_greeting = query_lower in GREETINGS or (
            len(query_lower.split()) <= 3 and any(query_lower.startswith(g) for g in GREETINGS)
        )

        if is_greeting:
            query_type = "chat"
        elif any(word in query_lower for word in SALES_TRIGGERS):
            query_type = "sales"
            data = self._get_sales_data(query_lower)
        elif any(word in query_lower for word in INVENTORY_TRIGGERS):
            query_type = "inventory"
            data = self._get_inventory_data(query_lower)
        elif any(word in query_lower for word in USER_TRIGGERS):
            query_type = "users"
            data = self._get_user_data(query_lower)
        elif any(word in query_lower for word in SUMMARY_TRIGGERS):
            query_type = "summary"
            data = self._get_summary_data()
        else:
            query_type = "chat"

        response = self._generate_response(query, data, query_type)
        self._save_conversation(query, response, conversation_id)

        return {
            'response': response,
            'tool_results': data,
            'agent_used': f'ai_assistant_{query_type}'
        }

    def _get_sales_data(self, query: str) -> Dict:
        data = {}
        if 'today' in query or 'daily' in query:
            data['today'] = self.tools.get_today_sales()
        if 'week' in query or 'weekly' in query:
            data['weekly'] = self.tools.get_weekly_sales()
        if 'month' in query or 'monthly' in query:
            data['monthly'] = self.tools.get_monthly_sales()
        if 'revenue' in query or 'total' in query:
            data['total'] = self.tools.get_total_revenue()
        if 'top' in query or 'best' in query or 'sold' in query or 'popular' in query:
            data['top'] = self.tools.get_top_selling_products()
        if not data:
            data['today'] = self.tools.get_today_sales()
            data['top'] = self.tools.get_top_selling_products()
        return data

    def _get_inventory_data(self, query: str) -> Dict:
        data = {}
        if 'status' in query or 'overview' in query:
            data['status'] = self.tools.get_inventory_status()
        if 'low' in query or 'alert' in query:
            data['low_stock'] = self.tools.get_low_stock_products()
        if 'restock' in query or 'reorder' in query:
            data['recommendations'] = self.tools.get_restocking_recommendations()
        if not data:
            data['status'] = self.tools.get_inventory_status()
            data['low_stock'] = self.tools.get_low_stock_products()
        return data

    def _get_user_data(self, query: str) -> Dict:
        data = {}
        if 'total' in query or 'count' in query:
            data['total'] = self.tools.get_total_users()
        if 'role' in query:
            data['roles'] = self.tools.get_users_by_role()
        if 'activity' in query:
            data['activity'] = self.tools.get_user_activity_summary()
        if not data:
            data['total'] = self.tools.get_total_users()
            data['roles'] = self.tools.get_users_by_role()
        return data

    def _get_summary_data(self) -> Dict:
        return self.tools.generate_business_summary()

    def _get_client_and_model(self, settings):
        import openai

        groq_key = getattr(settings, 'GROQ_API_KEY', None)
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)

        if groq_key:
            client = openai.OpenAI(api_key=groq_key, base_url='https://api.groq.com/openai/v1', timeout=15.0)
            return client, 'llama-3.3-70b-versatile'
        elif openai_key:
            model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            client = openai.OpenAI(api_key=openai_key, timeout=15.0)
            return client, model
        return None, None

    def _generate_response(self, query: str, data: Dict, query_type: str) -> str:
        """Generate a response using an OpenAI-compatible API, with conversation memory and retry."""

        try:
            from django.conf import settings

            client, model = self._get_client_and_model(settings)
            if client is None:
                return self._format_fallback_response(data, query_type)

            if query_type == "chat":
                system_prompt = (
                    "You are Mayondo AI, a friendly assistant for the Mayondo Wood and Furniture System. "
                    "Respond briefly and warmly to greetings and casual conversation. "
                    "Do not include any business data, statistics, or reports unless the user actually "
                    "asks a specific business question. Keep replies to 1-2 short sentences. "
                    + NO_MARKDOWN_INSTRUCTION
                )
                messages = [{"role": "system", "content": system_prompt}]
                for msg in self.conversation_history[-10:]:
                    if msg.get('role') in ('user', 'assistant'):
                        messages.append({"role": msg['role'], "content": msg['content']})
                messages.append({"role": "user", "content": query})

                last_error = None
                for attempt in range(2):
                    try:
                        response = client.chat.completions.create(
                            model=model, messages=messages, temperature=0.5, max_tokens=100
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        last_error = e
                        logger.warning(f"AI call failed (attempt {attempt + 1}/2): {e}")
                raise last_error

            data_str = json.dumps(data, default=str, indent=2)
            if len(data_str) > 6000:
                data_str = data_str[:6000] + "\n... (truncated)"

            system_prompt = (
                "You are Mayondo AI, an intelligent assistant for the Mayondo Wood and Furniture System. "
                "You help managers understand their business performance, sales, inventory, and users. "
                "Be professional, concise, and helpful. Use the data provided to answer questions. "
                "Always provide actionable insights. If the data shows low stock, recommend restocking. "
                "If sales are trending up or down, mention it. Be friendly but professional. "
                + NO_MARKDOWN_INSTRUCTION
            )

            user_prompt = f"""User Question: {query}

Business Data:
{data_str}

Please provide a helpful, professional response based on this data."""

            messages = [{"role": "system", "content": system_prompt}]
            for msg in self.conversation_history[-10:]:
                if msg.get('role') in ('user', 'assistant'):
                    messages.append({"role": msg['role'], "content": msg['content']})
            messages.append({"role": "user", "content": user_prompt})

            last_error = None
            for attempt in range(2):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=500
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    last_error = e
                    logger.warning(f"AI call failed (attempt {attempt + 1}/2): {e}")

            raise last_error

        except Exception as e:
            logger.error(f"AI API error: {e}")
            return self._format_fallback_response(data, query_type)

    def _format_fallback_response(self, data: Dict, query_type: str) -> str:
        """Fallback response when no AI provider is configured"""

        if query_type == "chat":
            return "Hello! How can I help you with your business today?"

        lines = []

        if query_type == "sales":
            lines.append("Sales Report\n")
            if 'today' in data:
                today = data['today']
                lines.append("Today's Sales:")
                lines.append(f"- Revenue: UGX {today.get('total_revenue', 0):,.2f}")
                lines.append(f"- Sales: {today.get('total_sales', 0)}")
                lines.append("")
            if 'top' in data and data['top']:
                lines.append("Top Products:")
                for p in data['top'][:3]:
                    lines.append(f"- {p.get('productname__productname', 'Unknown')}")

        elif query_type == "inventory":
            lines.append("Inventory Report\n")
            if 'status' in data:
                status = data['status']
                lines.append("Inventory Overview:")
                lines.append(f"- Products: {status.get('total_products', 0)}")
                lines.append(f"- Total Value: UGX {status.get('total_value', 0):,.2f}")
                lines.append("")
            if 'low_stock' in data:
                low = data['low_stock']
                if low:
                    lines.append(f"Low Stock Alert ({len(low)} items):")
                    for item in low[:5]:
                        lines.append(f"- {item.get('product', 'Unknown')}: {item.get('quantity', 0)} units")

        elif query_type == "users":
            lines.append("User Report\n")
            if 'total' in data:
                lines.append(f"Total Users: {data['total'].get('total_users', 0)}")
            if 'roles' in data:
                lines.append("\nUsers by Role:")
                for role, count in data['roles'].items():
                    lines.append(f"- {role.title()}: {count}")

        else:
            lines.append("Business Summary\n")
            if 'summary' in data:
                s = data['summary']
                lines.append(f"- Today's Revenue: UGX {s.get('total_revenue_today', 0):,.2f}")
                lines.append(f"- Monthly Revenue: UGX {s.get('monthly_revenue', 0):,.2f}")
                lines.append(f"- Inventory Value: UGX {s.get('total_inventory_value', 0):,.2f}")

        lines.append("\n---")
        lines.append("AI Assistant is running in offline mode.")

        return "\n".join(lines)

    def _save_conversation(self, query: str, response: str, conversation_id: int = None):
        from .models import Conversation, Message

        try:
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id, user=self.user)
            else:
                conversation = Conversation.objects.create(
                    user=self.user,
                    title=query[:50] + ('...' if len(query) > 50 else '')
                )

            Message.objects.create(conversation=conversation, role='user', content=query)
            Message.objects.create(conversation=conversation, role='assistant', content=response)

            from .models import UserPreference
            pref, _ = UserPreference.objects.get_or_create(user=self.user)
            pref.last_interaction = timezone.now()
            pref.save()

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
