from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from home.models import Stock, Sales, User, Profile
from typing import Dict, List, Any, Optional

class BusinessTools:
    """Collection of tools for AI agents to interact with the system"""
    
    def __init__(self, user=None):
        self.user = user
    
    # ============ SALES TOOLS ============
    
    def get_today_sales(self) -> Dict[str, Any]:
        """Get today's sales summary"""
        today = timezone.now().date()
        today_sales = Sales.objects.filter(date=today)
        
        return {
            'total_sales': today_sales.count(),
            'total_revenue': float(today_sales.aggregate(Sum('totalprice'))['totalprice__sum'] or 0),
            'total_items': today_sales.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'date': str(today)
        }
    
    def get_weekly_sales(self) -> Dict[str, Any]:
        """Get weekly sales summary (last 7 days)"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        weekly_sales = Sales.objects.filter(date__gte=week_ago, date__lte=today)
        previous_week = Sales.objects.filter(
            date__gte=week_ago - timedelta(days=7),
            date__lt=week_ago
        )
        
        current_total = weekly_sales.aggregate(Sum('totalprice'))['totalprice__sum'] or 0
        previous_total = previous_week.aggregate(Sum('totalprice'))['totalprice__sum'] or 0
        
        percent_change = 0
        if previous_total > 0:
            percent_change = ((current_total - previous_total) / previous_total) * 100
        
        return {
            'total_sales': weekly_sales.count(),
            'total_revenue': float(current_total),
            'revenue_change_percent': float(percent_change),
            'period_start': str(week_ago),
            'period_end': str(today),
            'previous_period_revenue': float(previous_total)
        }
    
    def get_monthly_sales(self) -> Dict[str, Any]:
        """Get monthly sales summary"""
        now = timezone.now()
        first_day = now.replace(day=1).date()
        
        monthly_sales = Sales.objects.filter(date__gte=first_day)
        
        # Get top selling products
        top_products = Sales.objects.filter(date__gte=first_day).values(
            'productname__productname'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('totalprice')
        ).order_by('-total_revenue')[:5]
        
        return {
            'total_sales': monthly_sales.count(),
            'total_revenue': float(monthly_sales.aggregate(Sum('totalprice'))['totalprice__sum'] or 0),
            'total_items': monthly_sales.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'month': first_day.strftime('%B %Y'),
            'top_products': list(top_products)
        }
    
    def get_total_revenue(self) -> Dict[str, Any]:
        """Get total revenue"""
        total = Sales.objects.aggregate(Sum('totalprice'))['totalprice__sum'] or 0
        total_count = Sales.objects.count()
        
        return {
            'total_revenue': float(total),
            'total_sales': total_count
        }
    
    def get_top_selling_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top selling products"""
        top_products = Sales.objects.values(
            'productname__productname',
            'productname__id'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('totalprice')
        ).order_by('-total_sold')[:limit]
        
        return list(top_products)
    
    def get_sales_by_product(self, product_name: str) -> Dict[str, Any]:
        """Get sales data for a specific product"""
        sales = Sales.objects.filter(productname__productname__icontains=product_name)
        
        return {
            'product': product_name,
            'total_sales': sales.count(),
            'total_quantity': sales.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'total_revenue': float(sales.aggregate(Sum('totalprice'))['totalprice__sum'] or 0)
        }
    
    # ============ INVENTORY TOOLS ============
    
    def get_inventory_status(self) -> Dict[str, Any]:
        """Get overall inventory status"""
        total_items = Stock.objects.count()
        total_value = Stock.objects.aggregate(Sum('costprice'))['costprice__sum'] or 0
        total_quantity = Stock.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        # Get products by grade
        by_grade = {}
        for grade in ['A', 'B', 'C']:
            count = Stock.objects.filter(quality=grade).count()
            if count > 0:
                by_grade[f'Grade {grade}'] = count
        
        return {
            'total_products': total_items,
            'total_quantity': total_quantity,
            'total_value': float(total_value),
            'products_by_grade': by_grade
        }
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get products with low stock"""
        low_stock = Stock.objects.filter(quantity__lt=threshold).order_by('quantity')
        
        return [{
            'id': item.id,
            'product': item.productname,
            'quantity': item.quantity,
            'grade': item.quality,
            'origin': item.origin
        } for item in low_stock]
    
    def get_stock_by_product(self, product_name: str) -> Dict[str, Any]:
        """Get stock details for a specific product"""
        stock = Stock.objects.filter(productname__icontains=product_name).first()
        
        if not stock:
            return {'product': product_name, 'found': False}
        
        return {
            'found': True,
            'product': stock.productname,
            'quantity': stock.quantity,
            'grade': stock.quality,
            'origin': stock.origin,
            'warehouse': stock.warehouse,
            'costprice': float(stock.costprice)
        }
    
    def get_restocking_recommendations(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get restocking recommendations"""
        low_stock = Stock.objects.filter(quantity__lt=threshold)
        
        recommendations = []
        for item in low_stock:
            recommended_qty = threshold * 2 - item.quantity
            recommendations.append({
                'product': item.productname,
                'current_stock': item.quantity,
                'recommended_restock': recommended_qty,
                'priority': 'High' if item.quantity < 5 else 'Medium',
                'grade': item.quality
            })
        
        return recommendations
    
    # ============ USER TOOLS ============
    
    def get_total_users(self) -> Dict[str, Any]:
        """Get total number of registered users"""
        total = User.objects.count()
        
        return {
            'total_users': total
        }
    
    def get_users_by_role(self) -> Dict[str, Any]:
        """Get users grouped by role"""
        roles = Profile.objects.values('role').annotate(count=Count('id'))
        
        result = {}
        for role in roles:
            result[role['role']] = role['count']
        
        return result
    
    def get_user_activity_summary(self) -> Dict[str, Any]:
        """Get user activity summary"""
        total = User.objects.count()
        
        # Users who have logged in recently (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active = User.objects.filter(last_login__gte=thirty_days_ago).count()
        
        roles = Profile.objects.values('role').annotate(count=Count('id'))
        
        return {
            'total_users': total,
            'active_users_last_30_days': active,
            'roles': {r['role']: r['count'] for r in roles}
        }
    
    def get_user_details(self, username: str) -> Dict[str, Any]:
        """Get details for a specific user"""
        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.filter(user=user).first()
            
            return {
                'found': True,
                'username': user.username,
                'email': user.email,
                'role': profile.role if profile else 'Unknown',
                'last_login': str(user.last_login),
                'date_joined': str(user.date_joined)
            }
        except User.DoesNotExist:
            return {'found': False, 'username': username}
    
    # ============ REPORTING TOOLS ============
    
    def generate_business_summary(self) -> Dict[str, Any]:
        """Generate a complete business summary"""
        today_sales = self.get_today_sales()
        monthly_sales = self.get_monthly_sales()
        inventory = self.get_inventory_status()
        low_stock = self.get_low_stock_products()
        top_products = self.get_top_selling_products()
        
        return {
            'date': str(timezone.now().date()),
            'today_sales': today_sales,
            'monthly_sales': monthly_sales,
            'inventory': inventory,
            'low_stock_items': len(low_stock),
            'top_products': top_products,
            'summary': {
                'total_revenue_today': today_sales['total_revenue'],
                'monthly_revenue': monthly_sales['total_revenue'],
                'total_inventory_value': inventory['total_value'],
                'products_low_stock': len(low_stock)
            }
        }
    
    # ============ INSIGHT GENERATION ============
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate business insights"""
        insights = []
        
        # Sales insights
        monthly = self.get_monthly_sales()
        if monthly['total_revenue'] > 0:
            insights.append({
                'type': 'sales',
                'title': 'Monthly Sales Performance',
                'description': f"Revenue this month: {monthly['total_revenue']:.2f}",
                'data': monthly
            })
        
        # Low stock alerts
        low_stock = self.get_low_stock_products()
        if low_stock:
            product_names = [item['product'] for item in low_stock[:3]]
            insights.append({
                'type': 'alert',
                'title': f'{len(low_stock)} Products Low in Stock',
                'description': f"Products low in stock: {', '.join(product_names)}",
                'data': {'low_stock_count': len(low_stock), 'products': low_stock}
            })
        
        # Top products
        top = self.get_top_selling_products()
        if top:
            insights.append({
                'type': 'recommendation',
                'title': 'Top Selling Products',
                'description': f"Best seller: {top[0]['productname__productname'] if top else 'None'}",
                'data': {'top_products': top}
            })
        
        return insights
