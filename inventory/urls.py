from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/sell/', views.sell_product, name='sell_product'),  # Changed from sell_product/<int:product_id>/
    path('sales/', views.sales_report, name='sales_report'),
    path('products/sell/<int:product_id>/', views.sell_product, name='sell_product'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('record-sale/', views.record_sale, name='record_sale'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),


]