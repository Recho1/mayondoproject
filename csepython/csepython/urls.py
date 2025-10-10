"""
URL configuration for csepython project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home.views import indexpage,stockpage,loginpage,registerpage,salespage,allsalespage,allstockpage,alluserspage,viewSingleSale,viewSingleStock,viewSingleUser,updatesale,deletestock,updatestock,deletesale,dashboardpage,updateuser,deleteuser,sale_receipt,logoutpage,monthly_stock_report,allsalesreport

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',indexpage,name='home'),
    path('stock/',stockpage),
    path('login/',loginpage, name='login'),
    path('register/',registerpage,name='register'),
    path('sales/',salespage,name='sales'),
    path('allsales/',allsalespage,name='allsales'),
    path('allstock/',allstockpage,name='allstock'),
    path('allusers/',alluserspage,name='allusers'),
    path('dashboard',dashboardpage,name='dashboard'),
    path('logout/',logoutpage,name='logout'),
    path('monthlyreport/',monthly_stock_report, name='monthly_stock_report'),
    path('salesreport/', allsalesreport, name='allsales'),

   

    # dynamic url
    path('stock/view/<str:stock_id>',viewSingleStock),
    path('sales/view/<str:sale_id>',viewSingleSale,name="view_sale"),
    path('view/user/<str:user_id>',viewSingleUser),
    path('sales/update/<str:sale_id>',updatesale),
    path('sales/delete/<str:sale_id>',deletesale),
    path('stock/delete/<str:stock_id>',deletestock),
    path('stock/update/<str:stock_id>',updatestock,name="update_stock"),
    path('register/update/<int:user_id>',updateuser,name="update_user"),
    path('register/delete/<str:user_id>',deleteuser,name="delete_user"),
    path('sales/receipt/<int:sale_id>/', sale_receipt, name='sale_receipt'),
    

]
