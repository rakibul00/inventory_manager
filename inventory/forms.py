from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Category, Sale

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'quantity', 
                 'purchase_price', 'selling_price', 'reorder_level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity_sold', 'customer_name', 'customer_contact']
    
    def __init__(self, user, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(created_by=user)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        
        


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity_sold', 'customer_name', 'customer_contact']
    
    def __init__(self, user, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(created_by=user)
        
        # If product_id is passed in GET parameters
        product_id = self.data.get('product_id') or kwargs.get('initial', {}).get('product_id')
        if product_id:
            self.fields['product'].initial = product_id
            self.fields['product'].widget.attrs['readonly'] = True
            self.fields['product'].disabled = True
            
            
            
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name
    
    
class RecordSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity_sold']