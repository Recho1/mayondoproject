from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import SignUp, Stock, Sales
from django.db.models import Sum
from datetime import datetime
import calendar
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
import json
from decimal import Decimal

def indexpage(request):
    return render(request, "index.html")

def loginpage(request):
    error = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dashboard')
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
        if password != repeat_password:
            errors['password'] = "Passwords do not match"
        elif User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists"
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            return redirect('/login/')
    return render(request, "register.html", {"errors": errors})

def logoutpage(request):
    logout(request)
    return redirect('/login/')

def dashboardpage(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    context = {
        'total_stock': Stock.objects.count(),
        'total_sales': Sales.objects.count(),
        'total_users': User.objects.count(),
        'user': request.user
    }
    return render(request, "dashboard.html", context)

def stockpage(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "stock.html")

def salespage(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    stocks = Stock.objects.all()
    agents = SignUp.objects.all()
    return render(request, "sales.html", {"stocks": stocks, "agents": agents})

def allsalespage(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "allsales.html")

def allstockpage(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "allstock.html")

def alluserspage(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "allusers.html")

def viewSingleStock(request, stock_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "view_stock.html", {"stock_id": stock_id})

def viewSingleSale(request, sale_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "view_sale.html", {"sale_id": sale_id})

def viewSingleUser(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "view_user.html", {"user_id": user_id})

def updatesale(request, sale_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "update_sale.html", {"sale_id": sale_id})

def updatestock(request, stock_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "update_stock.html", {"stock_id": stock_id})

def updateuser(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "update_user.html", {"user_id": user_id})

def sale_receipt(request, sale_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "sale_receipt.html", {"sale_id": sale_id})

def monthly_stock_report(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "monthly_stock_report.html")

def allsalesreport(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, "allsalesreport.html")
