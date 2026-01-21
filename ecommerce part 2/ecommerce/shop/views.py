from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from .forms import BuyerSignUpForm, VendorSignUpForm, StoreForm, ProductForm, ReviewForm
from .models import Shop, Product, CartItem, Invoice, Review, Order
from .utils.twitter_client import tweet_with_optional_image


# ----------------------------
# General and Authentication Views
# ----------------------------

def homepage(request):
    """Render the homepage."""
    return render(request, 'homepage.html')


def is_buyer(user):
    """Helper function to check if user is a buyer."""
    return user.is_authenticated and getattr(user, 'is_buyer', False)


# ----------------------------
# User Registration Views
# ----------------------------

def register_buyer(request):
    """
    Handle buyer registration.
    Assigns is_buyer flag and logs user in after signup.
    """
    if request.method == 'POST':
        form = BuyerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('all_products')
    else:
        form = BuyerSignUpForm()
    return render(request, 'shop/register.html', {'form': form})


def register_vendor(request):
    """
    Handle vendor registration.
    Assigns is_vendor flag and logs user in after signup.
    """
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my_stores')
    else:
        form = VendorSignUpForm()
    return render(request, 'shop/register.html', {'form': form})


# ----------------------------
# Vendor Views
# ----------------------------

@user_passes_test(lambda u: u.is_vendor)
def my_stores(request):
    """Display all stores owned by the logged-in vendor."""
    stores = Shop.objects.filter(owner=request.user)
    return render(request, 'shop/my_stores.html', {'stores': stores})


@csrf_exempt
@user_passes_test(lambda u: u.is_vendor)
def create_store(request):
    """Allow vendors to create a new store. Tweets on creation."""
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()

            message = f"🛍️ New Shop: {shop.name}\n{shop.description}"
            tweet_with_optional_image(message)

            return redirect("my_stores")
    else:
        form = StoreForm()
    return render(request, "shop/create_store.html", {"form": form})


@csrf_exempt
@user_passes_test(lambda u: u.is_vendor)
def add_product(request, shop_id):
    """
    Allow vendors to add a product to their store.
    Posts to Twitter on success.
    """
    shop = get_object_or_404(Shop, id=shop_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()

            message = f"📦 New Product in {product.shop.name}!\n{product.name} - {product.description}"
            tweet_with_optional_image(message)

            return redirect('product_list', shop_id=shop.id)
    else:
        form = ProductForm()

    return render(request, 'shop/add_product.html', {'form': form, 'shop': shop})


@user_passes_test(lambda u: u.is_vendor)
def edit_store(request, shop_id):
    """Allow vendors to update their store details."""
    store = get_object_or_404(Shop, id=shop_id, owner=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('my_stores')
    else:
        form = StoreForm(instance=store)
    return render(request, 'shop/edit_store.html', {'form': form, 'store': store})


@user_passes_test(lambda u: u.is_vendor)
def delete_store(request, shop_id):
    """Allow vendors to delete their store."""
    store = get_object_or_404(Shop, id=shop_id, owner=request.user)
    if request.method == 'POST':
        store.delete()
        return redirect('my_stores')
    return render(request, 'shop/delete_store.html', {'store': store})


@user_passes_test(lambda u: u.is_vendor)
def edit_product(request, product_id):
    """Allow vendors to edit a product."""
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list', shop_id=product.shop.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/edit_product.html', {'form': form, 'product': product})


@user_passes_test(lambda u: u.is_vendor)
def delete_product(request, product_id):
    """Allow vendors to delete a product."""
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('my_stores')
    return render(request, 'shop/delete_product.html', {'product': product})


# ----------------------------
# Buyer Views
# ----------------------------

@login_required
def product_list(request, shop_id):
    """Display all products in a selected store."""
    shop = get_object_or_404(Shop, id=shop_id)
    products = Product.objects.filter(shop=shop)
    return render(request, 'shop/product_list.html', {'shop': shop, 'products': products})


@user_passes_test(is_buyer)
@login_required
def add_to_cart(request, product_id):
    """Allow buyers to add a product to their cart."""
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('product_list', shop_id=product.shop.id)


@user_passes_test(is_buyer)
@login_required
def view_cart(request):
    """View current items in the buyer’s cart."""
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


@user_passes_test(is_buyer)
@login_required
def checkout(request):
    """
    Finalize order, generate invoice, email it, and clear the cart.
    """
    items = CartItem.objects.filter(user=request.user)
    invoice_text = ""

    for item in items:
        product = item.product
        quantity = item.quantity
        line_total = product.price * quantity

        Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            date_ordered=datetime.now()
        )

        invoice_text += f"{product.name} x {quantity} = {line_total}\n"

    # Create and store invoice
    Invoice.objects.create(user=request.user, content=invoice_text)

    # Send invoice via email
    send_mail(
        'Your Invoice',
        invoice_text,
        'store@example.com',
        [request.user.email]
    )

    # Clear cart after order
    items.delete()

    return render(request, 'shop/checkout_success.html')


def all_products(request):
    """View all products from all shops."""
    products = Product.objects.all()
    return render(request, 'shop/all_products.html', {'products': products})


@user_passes_test(is_buyer)
@login_required
def add_review(request, product_id):
    """Allow buyers to add a review if they haven’t already."""
    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('product_detail', product_id=product.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            has_ordered = Order.objects.filter(user=request.user, product=product).exists()

            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.is_verified = has_ordered
            review.save()

            messages.success(request, 'Your review has been submitted.')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'shop/add_review.html', {'form': form, 'product': product})


def product_detail(request, product_id):
    """Show product details and reviews. Allow review submission if not already reviewed."""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.review_set.all().order_by('-created_at')
    form = None

    if request.user.is_authenticated:
        if not Review.objects.filter(user=request.user, product=product).exists():
            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    has_ordered = Order.objects.filter(user=request.user, product=product).exists()

                    review = form.save(commit=False)
                    review.user = request.user
                    review.product = product
                    review.is_verified = has_ordered
                    review.save()

                    messages.success(request, "Thank you for your review!")
                    return redirect('product_detail', product_id=product.id)
            else:
                form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'shop/product_detail.html', context)
