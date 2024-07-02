from rest_framework import serializers
from .models import Customer, Product, Cart, CartItem

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customerId', 'username', 'name', 'email', 'phone']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product
        fields = ['productId', 'name', 'description', 'price', 'stockCount']
        
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta: 
        model = CartItem
        fields = ['cartItemId', 'product', 'quantity']
        
class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    # customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    
    class Meta: 
        model = Cart
        fields = ['id', 'customerId', 'status', 'items', 'createdAt']
        
    def get_items(self, obj):
            items = CartItem.objects.filter(cart=obj)
            return CartItemSerializer(items, many=True).data
        
    def validate_customerId(self, value):
        if Cart.objects.filter(customerId=value, status='open').exists():
            raise serializers.ValidationError("Customer already has an open cart, want to add to it?") 
        return value