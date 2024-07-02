from django.db import models
from django.core.exceptions import ValidationError

class Customer(models.Model):
    customerId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12)
    
    def __str__(self):
        return str(self.customerId)
    
class Product(models.Model):
    productId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stockCount = models.PositiveIntegerField()
    
    def __str__(self):
        return str(self.productId)
    
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    customerId = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='open')
    createdAt = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    cartItemId = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    
    def clean(self):
        if self.quantity is None:
            raise ValidationError('Quantity cannot be None')
        if self.product.stockCount is None:
            raise ValidationError('Product Stock cannot be None')
        
        if self.quantity > self.product.stockCount:
            raise ValidationError('Quantity exceed stock count')
        
        return self.quantity
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"