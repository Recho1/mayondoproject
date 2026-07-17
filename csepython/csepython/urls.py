from django.contrib import admin
from django.urls import path, include
from home.views import (
    indexpage, stockpage, loginpage, registerpage, salespage,
    allsalespage, allstockpage, alluserspage, viewSingleSale,
    viewSingleStock, viewSingleUser, updatesale, updatestock,
    dashboardpage, updateuser, sale_receipt, logoutpage,
    monthly_stock_report, allsalesreport,
    add_stock_page, add_sales_page,
    delete_stock, delete_sale, delete_user,
    analytics_page, stock_receipt, sales_report_pdf, stock_report_pdf
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),  # AI Assistant
    path('', indexpage, name='home'),
    path('register/', registerpage, name='register'),
    path('login/', loginpage, name='login'),
    path('logout/', logoutpage, name='logout'),
    path('dashboard/', dashboardpage, name='dashboard'),
    path('analytics/', analytics_page, name='analytics'),
    path('stock/', stockpage, name='stock'),
    path('allsales/', allsalespage, name='allsales'),
    path('allstock/', allstockpage, name='allstock'),
    path('allusers/', alluserspage, name='allusers'),
    path('sales/', salespage, name='sales'),
    path('monthlyreport/', monthly_stock_report, name='monthly_stock_report'),
    path('salesreport/', allsalesreport, name='salesreport'),
    
    # Add Stock and Sales Pages
    path('stock/add/', add_stock_page, name='add_stock'),
    path('sales/add/', add_sales_page, name='add_sales'),
    
    # CRUD Operations
    path('stock/delete/<int:stock_id>/', delete_stock, name='delete_stock'),
    path('sale/delete/<int:sale_id>/', delete_sale, name='delete_sale'),
    path('user/delete/<int:user_id>/', delete_user, name='delete_user'),
    
    # Dynamic URLs
    path('stock/view/<int:stock_id>/', viewSingleStock, name='view_stock'),
    path('sales/view/<int:sale_id>/', viewSingleSale, name='view_sale'),
    path('view/user/<int:user_id>/', viewSingleUser, name='view_user'),
    path('sales/update/<int:sale_id>/', updatesale, name='update_sale'),
    path('stock/update/<int:stock_id>/', updatestock, name='update_stock'),
    path('register/update/<int:user_id>/', updateuser, name='update_user'),
    path('sales/receipt/<int:sale_id>/', sale_receipt, name='sale_receipt'),
    path('stock/receipt/<int:stock_id>/', stock_receipt, name='stock_receipt'),
    path('salesreport/pdf/', sales_report_pdf, name='sales_report_pdf'),
    path('monthlyreport/pdf/', stock_report_pdf, name='stock_report_pdf'),
]
