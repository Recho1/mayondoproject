from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal, InvalidOperation
import re
from datetime import datetime
from django.contrib.auth import authenticate, login


# Stock is imported to enable us work with databases/access data base
from home.models import Stock
from home.models import Sales
from home.models import SignUp

# Create your views here.
def indexpage(request):
    return render (request,"index.html")
# here the method used is POST and submits the captured data

def stockpage(request):
    errors = {}
    if request.method == "POST":
        form_data = request.POST
        sent_productname = form_data.get('productname', '').strip()
        sent_origin = form_data.get('origin', '').strip()
        sent_contact = form_data.get('contact', '').strip()
        sent_quality = form_data.get('quality', '').strip()
        sent_quantity = form_data.get('quantity', '').strip()
        sent_unitcost = form_data.get('costprice_unitcost', '').strip()
        sent_date = form_data.get('date', '').strip()
        sent_warehouse = form_data.get('warehouse', '').strip()

        # --- Validation ---
        if not sent_productname:
            errors['productname'] = "Please enter productname."

        if not sent_origin:
            errors['origin'] = "Please enter supplier."

        if not sent_contact:
            errors['contact'] = "Please enter contact."

        if not sent_quality:
            errors['quality'] = "Please specify the quality."

        if not sent_quantity:
            errors['quantity'] = "Please enter quantity."
        else:
            try:
                sent_quantity = int(sent_quantity)
                if sent_quantity <=0:
                    errors['quantity'] = "Quantity must be greater than zero."
            except ValueError:
                errors['quantity'] = "Quantity must be a number."

        if not sent_unitcost:
            errors['costprice_unitcost'] = "Please enter the unitcost."
        else:
            try:
                sent_unitcost = int(sent_unitcost)
                if sent_unitcost <= 20000:
                    errors['costprice_unitcost'] = "Unit cost must be positive and above 20000."
            except ValueError:
                errors['costprice_unitcost'] = "Unit cost  is must be a number."

        if not sent_date:
            errors['date'] = "Please enter a date."
        else:
            try:
                input_date = datetime.strptime(sent_date, "%Y-%m-%d").date()
                today = datetime.now().date()
                if input_date > today:
                    errors['date'] = "Date cannot be in the future."
            except ValueError:
                errors['date'] = "Invalid date format."


        if not sent_warehouse:
            errors['warehouse'] = "Please enter the warehouse."

        # --- If errors, re-render form ---
        if errors:
            context = {
                'errors': errors,
                'form_data': form_data
            }
            return render(request, "stock.html", context)

        # --- Save Valid Data ---
        new_stock = Stock(
            productname=sent_productname,
            origin=sent_origin,
            contact=sent_contact,
            quality=sent_quality,
            quantity=sent_quantity,
            costprice_unitcost=sent_unitcost,
            costprice=sent_quantity * sent_unitcost,
            date=sent_date,
            warehouse=sent_warehouse
        )
        new_stock.save()
        return redirect('/allstock')

    return render(request, "stock.html")






def loginpage(request):
    error = None
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')


        try:
           selected_user = SignUp.objects.get(username=username)
           if selected_user.password == password:
                if selected_user.role == "manager":
                   request.session['role'] = 'manager'
                   return redirect('/dashboard')
                if selected_user.role == "salesagent":
                    request.session['role'] = 'salesagent'
                    return redirect('/sales')
           else:
                error = "Invalid username or password"
        except SignUp.DoesNotExist:
            error = "Invalid username"
    
    return render(request, "login.html", {"error": error})




def registerpage(request):
    errors = {}

    if request.method == "POST":
        form_data = request.POST
        username = form_data.get('username', '').strip()
        email = form_data.get('email', '').strip()
        password = form_data.get('password', '').strip()
        repeat_password = form_data.get('repeat_password', '').strip()
        role = form_data.get('role', '').strip()

        # --- Field Validations ---
        if not username:
            errors['username'] = "Username is required."
        elif SignUp.objects.filter(username=username).exists():
            errors['username'] = "This username already exists."

        if not email:
            errors['email'] = "Email is required."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors['email'] = "Invalid email format."
        elif SignUp.objects.filter(email=email).exists():
            errors['email'] = "This email is already exists."

        if not password:
            errors['password'] = "Please enter Password."

        if not repeat_password:
            errors['repeat_password'] = "Please confirm your password."
        elif password != repeat_password:
            errors['repeat_password'] = "Passwords do not match."

        if not role:
            errors['role'] = "Please select a role."

        # --- If errors, show form again ---
        if errors:
            context = {
                'errors': errors,
                'form_data': form_data,
            }
            return render(request, "register.html", context)

        # --- Save new user ---
        new_user = SignUp(
            username=username,
            email=email,
            password=password,  # You might want to hash this later
            role=role
        )
        new_user.save()

        messages.success(request, "User registered successfully.")
        return redirect('/allusers')

    # GET request
    return render(request, "register.html")





def salespage(request):
    if request.session.get('role') not in ['manager', 'salesagent']:
        return redirect('/login')
    role = request.session.get('role')
    all_products = Stock.objects.all()
    all_agents = SignUp.objects.filter(role='salesagent')
    errors = {}

    if request.method == "POST":
        form_data = request.POST

        # --- Clean and strip inputs ---
        sent_customername = form_data.get('customername', '').strip()
        sent_producttype = form_data.get('producttype', '').strip()
        form_productname = form_data.get('productname', '').strip()
        sent_quantity = form_data.get('quantity', '').strip()
        sent_unitcost = form_data.get('sellingprice_unitcost', '').strip()
        sent_transport_offered = form_data.get('transport_offered', '').strip()
        sent_is_paid = form_data.get('is_paid', '').strip()
        sent_paymentmethod = form_data.get('paymentmethod', '').strip()
        sent_date = form_data.get('date', '').strip()
        form_salesagentname = form_data.get('salesagentname', '').strip()

        # --- Field validation ---
        if not sent_customername:
            errors['customername'] = "Customer name should start with a capital."

        if not sent_producttype:
            errors['producttype'] = "Please fill in the producttype."

        if not form_productname:
            errors['productname'] = "Please select a product."
        else:
            try:
                sent_productname_obj = Stock.objects.get(id=form_productname)
            except Stock.DoesNotExist:
                errors['productname'] = "Selected product does not exist."

        if not sent_quantity:
            errors['quantity'] = "Please fill in the quantity."
        else:
            try:
                sent_quantity = int(sent_quantity)
                if sent_quantity <= 0:
                    errors['quantity'] = "Quantity must be greater than zero."
            except ValueError:
                errors['quantity'] = "Quantity must be a number."

        if not sent_unitcost:
            errors['sellingprice_unitcost'] = "Please enter unitcost."
        else:
            try:
                sent_unitcost = int(sent_unitcost)
                if sent_unitcost <= 15000:
                    errors['sellingprice_unitcost'] = "Unit cost must be greater than 15000."
            except ValueError:
                errors['sellingprice_unitcost'] = "Unit cost must be a number."

        if not form_salesagentname:
            errors['salesagentname'] = "Please select a sales agent."
        else:
            try:
                sent_salesagentname_obj = SignUp.objects.get(id=form_salesagentname)
            except SignUp.DoesNotExist:
                errors['salesagentname'] = "Selected sales agent does not exist."


        if not sent_date:
            errors['date'] = "Please enter a date."
        else:
            try:
                input_date = datetime.strptime(sent_date, "%Y-%m-%d").date()
                today = datetime.now().date()
                if input_date > today:
                    errors['date'] = "Date cannot be in the future."
            except ValueError:
                errors['date'] = "Invalid date format."

        
        # Check stock availability
        if 'productname' not in errors:
            if sent_productname_obj.quantity == 0:
                errors['quantity'] = f"Not enough stock for {sent_productname_obj.productname}. Available: {sent_productname_obj.quantity}"

        # If there are errors, render the template with errors
        if errors:
            context = {
                'all_products': all_products,
                'all_agents': all_agents,
                'errors': errors,
                'form_data': form_data,  # keep previously entered values
            }
            return render(request, "sales.html", context)

        # --- Calculate prices ---
        sent_sellingprice = sent_quantity * sent_unitcost
        if sent_transport_offered == '1':
            sent_transportfare = int(0.05 * sent_sellingprice)
            sent_transport_offered_bool = True
        else:
            sent_transportfare = 0
            sent_transport_offered_bool = False

        sent_totalprice = sent_sellingprice + sent_transportfare

        # --- Save sale ---
        new_sales = Sales(
            customername=sent_customername,
            producttype=sent_producttype,
            productname=sent_productname_obj,
            quantity=sent_quantity,
            sellingprice_unitcost=sent_unitcost,
            sellingprice=sent_sellingprice,
            paymentmethod=sent_paymentmethod,
            date=sent_date,
            salesagentname=sent_salesagentname_obj,
            transportfare=sent_transportfare,
            totalprice=sent_totalprice,
            transport_offered=sent_transport_offered_bool,
            is_paid=sent_is_paid == "True"  # convert string to bool
        )
        new_sales.save()

        # Update stock if paid
        if new_sales.is_paid:
            sent_productname_obj.quantity -= sent_quantity
            sent_productname_obj.save()

        return redirect('/allsales')

    # GET request
    context = {
        'all_products': all_products,
        'all_agents': all_agents,
        'role':role
    }
    return render(request, "sales.html", context)







def allsalespage(request):
    if request.session.get('role') not in ['manager', 'salesagent']:
        return redirect('/login')
    role = request.session.get('role')
    all_sales =Sales.objects.all()

    context ={
        "all_sales_details":all_sales,
        "role":role

    } 
         
    return render(request,"allsales.html",context)



def allstockpage(request):
    all_stock = Stock.objects.all()

    context = {
        "all_stock_details":all_stock
    }
    return render(request,"allstock.html",context)


def alluserspage(request):
    all_users = SignUp.objects.all()

    context = {
        "all_users_details":all_users
    }
    return render(request,"allusers.html",context)

# this function is for viewing a single stock
# a stock_id is passed so as to acess the stock using its id
def viewSingleStock(request,stock_id):
    selected = Stock.objects.get(id=stock_id)
    
    context = {
        "selected":selected
    }
    return render(request,"viewstock.html",context)

def viewSingleSale(request,sale_id):
    selected = Sales.objects.get(id=sale_id)

    context = {
        "selected":selected
    }
    
    return render(request,"viewsale.html",context)

def viewSingleUser(request,user_id):
    selected = SignUp.objects.get(id=user_id)

    context = {
        "selected":selected
    }
    return render(request,"singleuser.html",context)




        
        

#update sale
def updatesale(request,sale_id):
    sale_to_update = Sales.objects.get(id=sale_id)
    if request.method == "POST":
        
        form_data = request.POST
        sent_customername = form_data.get('customername')
        sent_producttype = form_data.get('producttype')
        form_productname = sale_to_update.productname
        sent_productname = form_data.get('productname')  
        sent_quantity = form_data.get('quantity')
        sent_unitcost = form_data.get('sellingprice_unitcost')
        sent_sellingprice = float(sent_quantity) * float(sent_unitcost)
        sent_transport_offered = form_data.get('transport_offered')
        sent_transportfare = form_data.get('transportfare')
        sent_is_paid = form_data.get('is_paid')
        print("sent_transport_offered")
        
        if sent_transport_offered == 'True':
            sent_transportfare = int(0.05 * sent_sellingprice)
        else:
            sent_transport_offered = False
            sent_transportfare = 0

        sent_totalprice = sent_sellingprice + sent_transportfare

        sent_paymentmethod = form_data.get('paymentmethod')
        sent_date = form_data.get('date')
        form_salesagentname = int(form_data.get('salesagentname'))
        sent_salesagentname = SignUp.objects.get(id=form_salesagentname)
        sent_productname = Stock.objects.get(id=sent_productname)
       


        
        sale_to_update.customername = sent_customername
        sale_to_update.producttype = sent_producttype
        sale_to_update.productname = sent_productname
        sale_to_update.quantity = sent_quantity
        sale_to_update.sellingprice_unitcost = sent_unitcost
        sale_to_update.sellingprice = sent_sellingprice
        sale_to_update.paymentmethod = sent_paymentmethod
        sale_to_update.date = sent_date
        sale_to_update.salesagentname = sent_salesagentname
        sale_to_update.transportfare = sent_transportfare
        sale_to_update.totalprice = sent_totalprice
        sale_to_update.transport_offered = sent_transport_offered
        sale_to_update.is_paid = sent_is_paid
        if sent_productname.quantity == 0 :
            context = {
                "error":'low stock for item'+ str(sent_productname.productname)
            }
            return render(request,"sales.html",context)
        sale_to_update.save()
        print(sent_is_paid)
        if sent_is_paid == 'True':
           edit_stock = sent_productname
           edit_stock.quantity = int(edit_stock.quantity) - int(sent_quantity)
           edit_stock.save()
        return redirect('/allsales')

    context = {
            "selected":sale_to_update,
            "products": Stock.objects.all(),
            "all_agents": SignUp.objects.all(),
            
            
        
        }

    return render(request,"updatesale.html",context)


# deleting stock
# def deletestock(request,stock_id):
#     stock_to_delete = Stock.objects.get(id=stock_id)
#     context = {
#             'selected':stock_to_delete,
#             'path_url':"allstock"
#     } 
#     if request.method == 'POST':
#         stock_to_delete.delete()
        

#         return redirect('/allstock')
#     return render(request,'delete.html',context)

# # delete sale
# def deletesale(request,sale_id):
#     sale_to_delete = Sales.objects.get(id=sale_id)
#     context = {
#             'selected':sale_to_delete,
#             'path_url':"allsales"

#     } 
#     if request.method == 'POST':
#         sale_to_delete.delete()
        

#         return redirect('/allsales')
#     return render(request,'delete.html',context)


def updateuser(request,user_id):
    user_to_update = SignUp.objects.get(id=user_id)
    
    context = {
           "selected":user_to_update
    }
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        repeat_password = request.POST.get('repeat_password')

        if password != repeat_password:
            messages.error(request, "passwords do not match")
            return render(request ,"register.html",context)
        
        if SignUp.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request,"username already exists")
            return render(request,"register.html",context)
        
        if SignUp.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request,"email already exists")
            return render(request,"register.html",context)
        
        user_to_update.username=username
        user_to_update.email=email
        user_to_update.password=password
        user_to_update.role=role
        user_to_update.repeat_password=repeat_password
        user_to_update.save()
        return redirect('/allusers/')
        
        
    return render (request,"updateuser.html",context)









# def deleteuser(request,user_id):
#     user_to_delete = SignUp.objects.get(id=user_id)
#     context = {
#             'selected':user_to_delete,
#             'path_url':"allusers"

#     } 
#     if request.method == 'POST':
#         user_to_delete.delete()
        

#         return redirect('/allusers')
#     return render(request,'delete.html',context)



# updating stock
def updatestock(request,stock_id):
    stock_to_update = Stock.objects.get(id=stock_id)
    context = {
           "selected":stock_to_update
    }
    if request.method == "POST":
       form_data = request.POST
       sent_productname = form_data.get('productname')
       sent_origin = form_data.get('origin') 
       sent_contact = form_data.get('contact')
       sent_quality = form_data.get('quality')
       sent_quantity = form_data.get('quantity')
       sent_costprice_unitcost = form_data.get('costprice_unitcost')
       sent_costprice = Decimal(sent_quantity) * Decimal(sent_costprice_unitcost)
       sent_date = form_data.get('date')
       sent_warehouse = form_data.get('warehouse')



       stock_to_update.productname = sent_productname
       stock_to_update.origin = sent_origin
       stock_to_update.contact = sent_contact
       stock_to_update.quality = sent_quality
       stock_to_update.quantity = sent_quantity
       stock_to_update.costprice_unitcost = sent_costprice_unitcost
       stock_to_update.costprice = sent_costprice
       stock_to_update.date = sent_date
       stock_to_update.warehouse = sent_warehouse

       stock_to_update.save()
       return redirect('/allstock')

       
    return render(request,"updatestock.html",context)


# dashboard

def dashboardpage(request):
    
    if request.session.get('role') != 'manager':
        return redirect('/login')
    total_stock = Stock.objects.aggregate(Sum('quantity'))['quantity__sum']
    if total_stock <= 500:

        stock_alert = "⚠️ Total stock is critically low (≤ 100). Please restock!"
    else:
        stock_alert = True
 
    total_sales = Sales.objects.aggregate(Sum('totalprice'))['totalprice__sum'] 
    daily_sales = Sales.objects.filter(date=timezone.now().date()).aggregate(Sum('totalprice'))['totalprice__sum']
    total_users = SignUp.objects.count() 
   
    total_costprice = Stock.objects.aggregate(Sum('costprice'))['costprice__sum']
    total_profit = int(total_sales) - int(total_costprice)

    
    completed_sales = Sales.objects.filter(is_paid="True").count()
    pending_sales =  Sales.objects.filter(is_paid="False").count()


    # Top-selling product considering the quantity sold
    top_product = (
        Sales.objects.values('productname__productname')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')
        .first()
    )
    top_selling_product = top_product['productname__productname'] if top_product else 'No sales yet'
     
     
# low_selling_product considering less than 5
    low_selling_product = (
    Sales.objects.values('productname__productname')
    .annotate(total_sold=Sum('quantity'))
    .filter(total_sold__lt=500)
    .order_by('total_sold')
)
    low_product = low_selling_product[0]['productname__productname'] if low_selling_product else 'no sales yet'
    # # Stock threshhold
    low_stock_count = Stock.objects.filter(quantity__lt=500)

    context = {
        'total_stock': total_stock,
        'total_sales': total_sales,
        'total_users':total_users,
        'daily_sales': daily_sales,
        'top_selling_product': top_selling_product,
        'low_selling_product':low_product,
        'stock_threshold': low_stock_count,
        "pending_sales": pending_sales,
        "completed_sales": completed_sales,
        "total_profit":total_profit,
        "stock_alert":stock_alert
        
    }
    return render(request, 'dashboard.html', context)



def sale_receipt(request, sale_id):
    selected = get_object_or_404(Sales, id=sale_id)

    # If the user clicked "Cancel", redirect back to All Sales
    if request.method == 'POST' and 'cancel' in request.POST:
        return redirect('/allsales/')

    # Otherwise, show the receipt page
    return render(request, 'receipt.html', {'selected': selected})


# def sale_receipt(request, sale_id):
    
#     selected = get_object_or_404(Sales, id=sale_id)

#     return redirect('/allsales')
    
    
#     return render(request, 'receipt.html', {'selected': selected})

# logout
def logoutpage(request):
    if request.method == 'POST':
        return redirect('login')
    return render(request,"logout.html")

# stock report
def monthly_stock_report(request):
    month = request.GET.get('month')
    all_stock_details = Stock.objects.all()
    selected_month = None

    if month:
        selected_month = datetime.strptime(month, "%Y-%m")
        all_stock_details = all_stock_details.filter(
            date__year=selected_month.year,
            date__month=selected_month.month
        )

    total_value = sum(s.costprice for s in all_stock_details)
    return render(request, 'stockreport.html', {
        'all_stock_details': all_stock_details,
        'total_value': total_value,
        'selected_month': month,
    })

# sales report


def allsalesreport(request):
    month = request.GET.get('month')
    sales = Sales.objects.all()
    selected_month = None

    if month:
        selected_month = datetime.strptime(month, "%Y-%m")
        sales = sales.filter(
            date__year=selected_month.year,
            date__month=selected_month.month
        )

    # Calculate totals
    total_quantity = sum(s.quantity for s in sales)
    total_sales = sum(s.totalprice for s in sales)

    return render(request, 'salesreport.html', {
        'all_sales_details': sales,
        'selected_month': selected_month,
        'total_quantity': total_quantity,
        'total_sales': total_sales,
    })



    


        



