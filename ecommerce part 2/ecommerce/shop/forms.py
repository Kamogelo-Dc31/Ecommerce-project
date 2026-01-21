from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Shop, Product, Review

# --- Custom Registration Form for Buyers ---
class BuyerSignUpForm(UserCreationForm):
    """
    A form used to register a new Buyer user.
    Inherits from Django's UserCreationForm and sets `is_buyer` to True.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_buyer = True  # Mark the user as a buyer
        if commit:
            user.save()
        return user


# --- Custom Registration Form for Vendors ---
class VendorSignUpForm(UserCreationForm):
    """
    A form used to register a new Vendor user.
    Inherits from Django's UserCreationForm and sets `is_vendor` to True.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_vendor = True  # Mark the user as a vendor
        if commit:
            user.save()
        return user


# --- Form for Creating/Editing a Store ---
class StoreForm(forms.ModelForm):
    """
    Form for vendors to create or update their shop.
    """
    class Meta:
        model = Shop
        fields = ['name', 'description']


# --- Form for Adding/Editing a Product ---
class ProductForm(forms.ModelForm):
    """
    Form for vendors to add or update products in their shops.
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity', 'image']


# --- Form for Submitting a Product Review ---
class ReviewForm(forms.ModelForm):
    """
    Form for buyers to submit a review and rating for a product.
    The 'is_verified' field is handled in the view based on order history.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
