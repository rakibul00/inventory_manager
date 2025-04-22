from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.http import JsonResponse
from .models import Product, Sale, Category
from .forms import ProductForm, SaleForm, CategoryForm, CustomUserCreationForm
from .forms import RecordSaleForm
from .utils import calculate_dashboard_stats

@login_required
def home(request):
    stats = calculate_dashboard_stats(request.user)
    
    # Calculate profit margin
    stats['profit_margin'] = 0
    if stats['total_sales_value'] > 0:
        stats['profit_margin'] = (stats['total_profit'] / stats['total_sales_value']) * 100
    
    # Get low stock products
    low_stock_products = Product.objects.filter(
        created_by=request.user,
        quantity__lte=F('reorder_level')
    ).order_by('quantity')[:5]
    
    # Recent sales
    recent_sales = Sale.objects.filter(
        sold_by=request.user
    ).select_related('product').order_by('-sale_date')[:5]
    
    context = {
        **stats,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
    }
    return render(request, 'inventory/home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'inventory/register.html', {'form': form})




def login_view(request):
     if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after login
        else:
            messages.error(request, 'Invalid username or password.')
     return render(request, 'inventory/login.html')
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required
def product_list(request):
    products = Product.objects.filter(created_by=request.user).select_related('category')
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/add_product.html', {'form': form})

@login_required
def sell_product(request):
    if request.method == 'POST':
        form = SaleForm(request.user, request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            product = sale.product
            
            if sale.quantity_sold > product.quantity:
                messages.error(request, f'Not enough stock available. Only {product.quantity} left.')
                return redirect('sell_product')
            
            sale.sold_by = request.user
            sale.save()
            
            # Update product quantity
            product.quantity -= sale.quantity_sold
            product.save()
            
            messages.success(request, f'Sale recorded successfully for {product.name}!')
            return redirect('home')
    else:
        form = SaleForm(request.user)
    
    
    
    return render(request, 'inventory/sell_product.html', {'form': form})

@login_required
def sales_report(request):
    sales = Sale.objects.filter(sold_by=request.user).select_related('product')
    total_sales = sales.aggregate(
        total_quantity=Sum('quantity_sold'),
        total_revenue=Sum(ExpressionWrapper(
            F('quantity_sold') * F('product__selling_price'),
            output_field=DecimalField()
        )),
        total_profit=Sum(ExpressionWrapper(
            F('quantity_sold') * (F('product__selling_price') - F('product__purchase_price')),
            output_field=DecimalField()
        ))
    )
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
    }
    return render(request, 'inventory/sales_report.html', context)

@login_required
def manage_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    categories = Category.objects.all()
    return render(request, 'inventory/manage_categories.html', {
        'form': form,
        'categories': categories
    })

@login_required
def get_product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id, created_by=request.user)
    data = {
        'name': product.name,
        'quantity': product.quantity,
        'selling_price': str(product.selling_price),
        'profit_per_unit': str(product.profit_per_unit()),
    }
    return JsonResponse(data)

@login_required
def sell_product(request):
    if request.method == 'POST':
        form = SaleForm(request.user, request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            product = sale.product
            
            if sale.quantity_sold > product.quantity:
                messages.error(request, f'Not enough stock available. Only {product.quantity} left.')
                return redirect('sell_product')
            
            sale.sold_by = request.user
            sale.save()
            
            # Update product quantity
            product.quantity -= sale.quantity_sold
            product.save()
            
            messages.success(request, f'Sale recorded successfully for {product.name}!')
            return redirect('sales_report')
    else:
        form = SaleForm(request.user)
    
    return render(request, 'inventory/sell_product.html', {'form': form})

@login_required
def product_list(request):
    products = Product.objects.filter(created_by=request.user).select_related('category')
    return render(request, 'inventory/product_list.html', {'products': products})


@login_required
def sales_report(request):
    sales = Sale.objects.filter(sold_by=request.user).select_related('product').order_by('-sale_date')
    
    total_sales = sales.aggregate(
        total_quantity=Sum('quantity_sold', default=0),
        total_revenue=Sum(
            ExpressionWrapper(
                F('quantity_sold') * F('product__selling_price'),
                output_field=DecimalField()
            ),
            default=0
        ),
        total_profit=Sum(
            ExpressionWrapper(
                F('quantity_sold') * (F('product__selling_price') - F('product__purchase_price')),
                output_field=DecimalField()
            ),
            default=0
        )
    )
    
    return render(request, 'inventory/sales_report.html', {
        'sales': sales,
        'total_sales': total_sales
    })
    
    
    
    
@login_required
def manage_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/manage_categories.html', {
        'form': form,
        'categories': categories
    })
    
    
    
def record_sale(request):
    if request.method == 'POST':
        form = RecordSaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            product = sale.product

            # Check stock availability
            if product.quantity >= sale.quantity_sold:
                product.quantity -= sale.quantity_sold
                product.save()

                # Calculate total sale amount and profit
            

                messages.success(request, f"Sale recorded successfully for {product.name}.")
                return redirect('sales_report')
            else:
                messages.error(request, f"Not enough stock for {product.name}.")
    else:
        form = RecordSaleForm()

    return render(request, 'inventory/record_sale.html', {'form': form})







@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('manage_categories')
    return render(request, 'inventory/delete_category.html', {'category': category})