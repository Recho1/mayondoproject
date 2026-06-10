from django.db import models
GRADE_CHOICES = [
    ('A','Grade A'),
    ('B','Grade B'),
    ('C','Grade C'),
]

# Create your models here.
class Login(models.Model):
    email = models.CharField(max_length=20)
    password = models.CharField(max_length=8)

class SignUp(models.Model):
    username = models.TextField(max_length=20)
    email = models.CharField(max_length=20)
    password = models.CharField(max_length=8)
    repeat_password = models.CharField(max_length=20)
    role = models.CharField(max_length=20)
    def __str__(self):
        return self.username
    

class Stock(models.Model):
    productname = models.TextField()
    origin = models.TextField()
    contact = models.IntegerField()
    quality = models.CharField(max_length=10,choices=GRADE_CHOICES,blank=True)
    quantity = models.IntegerField()
    costprice_unitcost = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    costprice = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    date = models.DateField(null=True)
    warehouse = models.TextField()
    def __str__(self):
        return  self.productname 
        
    

class Sales(models.Model):
    customername = models.TextField()
    producttype = models.CharField(max_length=20)
    productname = models.ForeignKey(Stock,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sellingprice_unitcost = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    sellingprice = models.DecimalField(max_digits=10,decimal_places=2)
    transportfare = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    transport_offered = models.BooleanField(default=True)
    paymentmethod = models.CharField(max_length=10)
    salesagentname = models.ForeignKey(SignUp,on_delete=models.CASCADE)
    date = models.DateField(null=True)
    totalprice = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    is_paid = models.BooleanField()






