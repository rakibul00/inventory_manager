from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Set to NULL when the user is deleted
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reorder_level = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.quantity} in stock)"
    
    def profit_per_unit(self):
        return self.selling_price - self.purchase_price
    
    def total_profit(self):
        return self.profit_per_unit() * self.quantity
    
    def stock_status(self):
        if self.quantity == 0:
            return "out-of-stock"
        elif self.quantity <= self.reorder_level:
            return "low-stock"
        return "in-stock"

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    sale_date = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_contact = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"{self.quantity_sold} of {self.product.name} sold on {self.sale_date}"
    
    def total_sale_amount(self):
        return self.product.selling_price * self.quantity_sold
    
    def total_cost(self):
        return self.product.purchase_price * self.quantity_sold
    
    def profit(self):
        return self.total_sale_amount() - self.total_cost()       
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        from .models import Product
        
        def sell_product(request, product_id):
            product = get_object_or_404(Product, id=product_id)
            if product.quantity > 0:
                product.quantity -= 1
                product.save()
                messages.success(request, f"{product.name} sold successfully!")
            else:
                messages.error(request, f"{product.name} is out of stock!")
            return redirect('product_list')