from django.contrib import admin
from .models import User, Shop, Product, CartItem, Review, Invoice
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_vendor', 'is_buyer', 'is_staff', 'is_superuser')
    list_filter = ('is_vendor', 'is_buyer', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_vendor', 'is_buyer')}),
    )

@admin.register(Shop)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    search_fields = ('name', 'owner__username')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price', 'quantity')
    search_fields = ('name', 'store__name')
    list_filter = ('shop',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'is_verified', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')  
    list_filter = ('is_verified', 'rating')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'content')
    readonly_fields = ('created_at',)
