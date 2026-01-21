from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# --- Custom User Model ---
class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds roles: is_vendor and is_buyer.
    """
    is_vendor = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)


# --- Shop Model ---
class Shop(models.Model):
    """
    Represents a shop/store owned by a vendor.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# --- Product Model ---
class Product(models.Model):
    """
    Represents a product listed in a shop.
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# --- Cart Item Model ---
class CartItem(models.Model):
    """
    Represents an item in a buyer's shopping cart.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# --- Order Model ---
class Order(models.Model):
    """
    Represents a completed purchase of a product by a user.
    Used to verify reviews.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order: {self.user} -> {self.product} (x{self.quantity})"


# --- Review Model ---
class Review(models.Model):
    """
    Represents a review submitted by a buyer for a product.
    Only one review per product per user is allowed.
    `is_verified` indicates if the buyer purchased the product.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent multiple reviews from the same user

    def __str__(self):
        return f"Review by {self.user} for {self.product}"


# --- Invoice Model ---
class Invoice(models.Model):
    """
    Stores invoice content generated after checkout.
    Sent to the user's email upon purchase.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.TextField()

    def __str__(self):
        return f"Invoice for {self.user} on {self.created_at.strftime('%Y-%m-%d')}"
