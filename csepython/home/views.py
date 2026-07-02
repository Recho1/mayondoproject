from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from .models import Stock, Sales, Profile
from datetime import datetime, date, timedelta
import json
from decimal import Decimal

# ============ HELPER FUNCTIONS ============
def is_manager(user):
    try:
        return user.profile.role == "manager"
    except:
        return False

def is_sales_agent(user):
    try:
        return user.profile.role == "salesagent"
    except:
        return False

# ============ PUBLIC VIEWS ============

def indexpage(request):
    context = {
        'total_stock': Stock.objects.count(),
        'total_sales': Sales.objects.count(),
        'total_users': User.objects.count(),
    }
    return render(request, "index_public.html", context)

def loginpage(request):
    error = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
                profile = user.profile
                if profile.role == "manager":
                    return redirect('/dashboard/')
                else:
                    return redirect('/sales/')
            except:
                return redirect('/')
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def registerpage(request):
    errors = {}
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')
        role = request.POST.get('role', 'salesagent')
        
        if password != repeat_password:
            errors['password'] = "Passwords do not match"
        elif User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists"
        elif User.objects.filter(email=email).exists():
            errors['email'] = "Email already exists"
        else:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            # Create profile with role (manager or salesagent)
            Profile.objects.create(user=user, role=role)
            return redirect('/login/')
    
    return render(request, "register.html", {"errors": errors})

def logoutpage(request):
    logout(request)
    return redirect('/login/')

# ============ DASHBOARD - MANAGER ONLY ============

@login_required(login_url='/login/')
def dashboardpage(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    
    # Get date ranges
    today = date.today()
    first_day_of_month = today.replace(day=1)
    last_30_days = today - timedelta(days=30)
    
    # Stock stats
    total_stock_items = Stock.objects.count()
    total_stock_value = Stock.objects.aggregate(Sum('costprice'))['costprice__sum'] or 0
    low_stock_items = Stock.objects.filter(quantity__lt=10)
    low_stock_count = low_stock_items.count()
    
    # Sales stats
    total_sales = Sales.objects.count()
    total_revenue = Sales.objects.aggregate(Sum('totalprice'))['totalprice__sum'] or 0
    sales_30_days = Sales.objects.filter(date__gte=last_30_days)
    revenue_30_days = sales_30_days.aggregate(Sum('totalprice'))['totalprice__sum'] or 0
    
    # Recent
    recent_stock = Stock.objects.all().order_by('-date')[:10]
    recent_sales = Sales.objects.all().order_by('-date')[:10]
    
    context = {
        'user': request.user,
        'is_manager': True,
        'total_stock_items': total_stock_items,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
        'low_stock_items': low_stock_items,
        'recent_stock': recent_stock,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'revenue_30_days': revenue_30_days,
        'recent_sales': recent_sales,
        'total_users': User.objects.count(),
    }
    
    return render(request, "dashboard.html", context)

# ============ MANAGER ONLY VIEWS ============

@login_required(login_url='/login/')
def stockpage(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    return render(request, "stock.html", {"is_manager": True})

@login_required(login_url='/login/')
def allstockpage(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    
    stock_items = Stock.objects.all().order_by('-date')
    search_query = request.GET.get('search')
    if search_query:
        stock_items = stock_items.filter(
            Q(productname__icontains=search_query) |
            Q(origin__icontains=search_query)
        )
    
    paginator = Paginator(stock_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'stock_items': page_obj,
        'total_stock': stock_items.count(),
        'search_query': search_query,
        'is_manager': True,
    }
    return render(request, "allstock.html", context)

@login_required(login_url='/login/')
def alluserspage(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    
    users = User.objects.all()
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'total_users': users.count(),
        'is_manager': True,
    }
    return render(request, "allusers.html", context)

@login_required(login_url='/login/')
def monthly_stock_report(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    
    today = date.today()
    monthly_stock = Stock.objects.filter(
        date__month=today.month,
        date__year=today.year
    )
    
    context = {
        'stock_items': monthly_stock,
        'month': today.strftime('%B %Y'),
        'total_items': monthly_stock.count(),
        'is_manager': True,
    }
    return render(request, "stockreport.html", context)

@login_required(login_url='/login/')
def allsalesreport(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    
    all_sales = Sales.objects.all()
    total_amount = all_sales.aggregate(Sum('totalprice'))['totalprice__sum'] or 0
    
    context = {
        'sales': all_sales,
        'total_amount': total_amount,
        'total_sales': all_sales.count(),
        'is_manager': True,
    }
    return render(request, "salesreport.html", context)

# ============ SALES AGENT VIEWS ============

@login_required(login_url='/login/')
def salespage(request):
    stocks = Stock.objects.all()
    agents = User.objects.all()
    
    context = {
        'stocks': stocks,
        'agents': agents,
        'user': request.user,
        'is_manager': is_manager(request.user),
    }
    return render(request, "sales.html", context)

@login_required(login_url='/login/')
def allsalespage(request):
    sales = Sales.objects.all().order_by('-date')
    search_query = request.GET.get('search')
    if search_query:
        sales = sales.filter(
            Q(customername__icontains=search_query) |
            Q(productname__productname__icontains=search_query)
        )
    
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'sales': page_obj,
        'total_sales': sales.count(),
        'search_query': search_query,
        'is_manager': is_manager(request.user),
    }
    return render(request, "allsales.html", context)

@login_required(login_url='/login/')
def viewSingleSale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    return render(request, "viewsale.html", {"sale": sale})

@login_required(login_url='/login/')
def updatesale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    if request.method == "POST":
        sale.customername = request.POST.get('customername')
        sale.quantity = request.POST.get('quantity')
        sale.save()
        return redirect('/allsales/')
    return render(request, "updatesale.html", {"sale": sale})

@login_required(login_url='/login/')
def sale_receipt(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    return render(request, "receipt.html", {"sale": sale})

# ============ CRUD OPERATIONS ============

@login_required(login_url='/login/')
def viewSingleStock(request, stock_id):
    if not is_manager(request.user):
        return redirect('/sales/')
    stock = get_object_or_404(Stock, id=stock_id)
    return render(request, "viewstock.html", {"stock": stock})

@login_required(login_url='/login/')
def viewSingleUser(request, user_id):
    if not is_manager(request.user):
        return redirect('/sales/')
    user = get_object_or_404(User, id=user_id)
    return render(request, "singleuser.html", {"user": user})

@login_required(login_url='/login/')
def updatestock(request, stock_id):
    if not is_manager(request.user):
        return redirect('/sales/')
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == "POST":
        stock.productname = request.POST.get('productname')
        stock.quantity = request.POST.get('quantity')
        stock.save()
        return redirect('/allstock/')
    return render(request, "updatestock.html", {"stock": stock})

@login_required(login_url='/login/')
def updateuser(request, user_id):
    if not is_manager(request.user):
        return redirect('/sales/')
    user = get_object_or_404(User, id=user_id)
    return render(request, "updateuser.html", {"user": user})

# ============ ADD STOCK ============

@login_required(login_url='/login/')
def add_stock_page(request):
    if not is_manager(request.user):
        return redirect('/sales/')
    
    if request.method == "POST":
        try:
            productname = request.POST.get('productname')
            origin = request.POST.get('origin')
            contact = int(request.POST.get('contact', 123456789))
            quantity = int(request.POST.get('quantity', 0))
            quality = request.POST.get('quality', 'A')
            cost_price = float(request.POST.get('costprice', 0))
            warehouse = request.POST.get('warehouse', 'Main')
            date_str = request.POST.get('date')
            
            if date_str:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                date_obj = date.today()
            
            stock = Stock.objects.create(
                productname=productname,
                origin=origin,
                contact=contact,
                quantity=quantity,
                quality=quality,
                costprice_unitcost=cost_price,
                costprice=cost_price * quantity,
                date=date_obj,
                warehouse=warehouse
            )
            
            return redirect('/allstock/')
            
        except Exception as e:
            print(f"Error adding stock: {e}")
            return render(request, "add_stock.html", {"error": str(e)})
    
    return render(request, "add_stock.html")

# ============ ADD SALE ============

@login_required(login_url='/login/')
def add_sales_page(request):
    if request.method == "POST":
        try:
            product_id = request.POST.get('productname')
            product = Stock.objects.get(id=product_id)
            quantity = int(request.POST.get('quantity'))
            
            if product.quantity < quantity:
                return render(request, "add_sales.html", {
                    "stocks": Stock.objects.all(),
                    "agents": User.objects.all(),
                    "error": "Not enough stock available!"
                })
            
            selling_price = float(request.POST.get('sellingprice', 0))
            total_price = selling_price * quantity
            date_str = request.POST.get('date')
            
            if date_str:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                date_obj = date.today()
            
            profile, created = Profile.objects.get_or_create(user=request.user, defaults={'role': 'salesagent'})
            
            sale = Sales.objects.create(
                customername=request.POST.get('customername'),
                productname=product,
                quantity=quantity,
                sellingprice=selling_price * quantity,
                sellingprice_unitcost=selling_price,
                transportfare=float(request.POST.get('transportfare', 0)),
                paymentmethod=request.POST.get('paymentmethod', 'cash'),
                salesagentname=request.user,
                date=date_obj,
                totalprice=total_price,
                is_paid=request.POST.get('is_paid', 'on') == 'on'
            )
            
            product.quantity -= quantity
            product.save()
            
            return redirect('/allsales/')
            
        except Exception as e:
            print(f"Error adding sale: {e}")
            return render(request, "add_sales.html", {
                "stocks": Stock.objects.all(),
                "agents": User.objects.all(),
                "error": str(e)
            })
    
    stocks = Stock.objects.all()
    agents = User.objects.all()
    return render(request, "add_sales.html", {"stocks": stocks, "agents": agents})

# ============ DELETE OPERATIONS ============

@login_required(login_url='/login/')
def delete_stock(request, stock_id):
    if not is_manager(request.user):
        return redirect('/sales/')
    stock = get_object_or_404(Stock, id=stock_id)
    stock.delete()
    return redirect('/allstock/')

@login_required(login_url='/login/')
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    sale.delete()
    return redirect('/allsales/')

@login_required(login_url='/login/')
def delete_user(request, user_id):
    if not is_manager(request.user):
        return redirect('/sales/')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('/allusers/')
