from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Customer, Product, Cart, CartItem
from .serializer import CustomerSerializer, ProductSerializer, CartSerializer, CartItemSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer endpoint that allows customers to be viewed or edited.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class ProductViewSet(viewsets.ModelViewSet):
    """
    Product endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class CartViewSet(viewsets.ModelViewSet):
    """
    Cart endpoint that allows carts to be viewed or edited.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Add an item to the cart.
        """
        cart = self.get_object()
        product_id = request.data.get('productId')
        quantity = request.data.get('quantity', 1)
        
        try: 
            quantity = int(quantity)
            if quantity <= 0:
                return Response({'error': 'Quantity must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
                return Response({'error': 'Quantity must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(productId=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'},  status=status.HTTP_400_BAD_REQUEST)
        
        if product.stockCount < quantity:
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if (cart_item.quantity + quantity) > 0:
                return Response({'error': 'Quantity exceeds Stock count'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = quantity
            
        cart_item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """
        Remove an item from the cart.
        """
        cart = self.get_object()
        product_id = request.data.get('productId')
        
        try: 
            product = Product.objects.get(productId=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        """
        Update the quantity of an item in the cart.
        """
        cart = self.get_object()
        product_id = request.data.get('productId')
        quantity = request.data.get('quantity')
        try:
            product = Product.objects.get(productId=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if product.stockCount < quantity:
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def checkout(self, request, pk=None):
        """
        Checkout the cart.
        """
        cart = self.get_object()
        if cart.status != 'open':
            return Response({'error': 'Cart is already checked out or closed'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = CartItem.objects.filter(cart=cart)

        for item in cart_items:
            product = item.product
            if product.stockCount < item.quantity:
                return Response({'error': f'Not enough stock for {product.name}'}, status=status.HTTP_400_BAD_REQUEST)
            product.stockCount -= item.quantity
            product.save()

        cart.status = 'checked_out'
        cart.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action (detail=True, methods=['GET'])
    def cart_items(self, request, pk=None):
        """
        Get items in the cart.
        """
        cart = self.get_object()
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)