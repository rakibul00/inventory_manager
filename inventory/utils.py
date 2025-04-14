from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Product, Sale

def calculate_dashboard_stats(user):
    # Initialize all variables with default values
    stats = {
        'total_products': 0,
        'total_items_in_stock': 0,
        'total_items_sold': 0,
        'total_purchase_value': 0,
        'total_sales_value': 0,
        'total_profit': 0,
        'profit_margin': 0,
    }

    # Product stats
    products = Product.objects.filter(created_by=user)
    product_stats = products.aggregate(
        total_products=Sum('quantity', default=0),
        total_purchase=Sum(
            ExpressionWrapper(
                F('quantity') * F('purchase_price'),
                output_field=DecimalField()
            ),
            default=0
        )
    )
    
    stats['total_products'] = products.count()
    stats['total_items_in_stock'] = product_stats['total_products']
    stats['total_purchase_value'] = product_stats['total_purchase']

    # Sales stats
    sales = Sale.objects.filter(sold_by=user)
    sales_stats = sales.aggregate(
        total_sold=Sum('quantity_sold', default=0),
        total_sales=Sum(
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
    
    stats['total_items_sold'] = sales_stats['total_sold']
    stats['total_sales_value'] = sales_stats['total_sales']
    stats['total_profit'] = sales_stats['total_profit']

    # Calculate profit margin (only if sales_value > 0)
    if stats['total_sales_value'] > 0:
        stats['profit_margin'] = (stats['total_profit'] / stats['total_sales_value']) * 100

    return stats