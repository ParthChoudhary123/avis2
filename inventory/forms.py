from django import forms
from django.contrib.auth import get_user_model
from .models import Product, Vendor, Order, Stock

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    # Vendor specific fields
    vendor_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor/Company Name'}))
    vendor_city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City (for weather tracking)'}))
    vendor_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 2}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        role = cleaned_data.get("role")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

        if role == 'vendor':
            if not cleaned_data.get('vendor_name'):
                self.add_error('vendor_name', 'Vendor name is required for vendor registration.')
            if not cleaned_data.get('vendor_city'):
                self.add_error('vendor_city', 'City is required for vendor registration.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
            if user.role == 'vendor':
                Vendor.objects.create(
                    user=user,
                    name=self.cleaned_data.get('vendor_name'),
                    email=user.email,
                    city=self.cleaned_data.get('vendor_city'),
                    address=self.cleaned_data.get('vendor_address')
                )
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'price']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'step': '0.01'}),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['current_quantity', 'min_threshold']
        widgets = {
            'current_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Quantity'}),
            'min_threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Safety Threshold'}),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'email', 'city', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'vendor', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
        }
