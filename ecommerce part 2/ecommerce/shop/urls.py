from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('register/vendor/', views.register_vendor, name='register_vendor'),
    path('stores/', views.my_stores, name='my_stores'),
    path('store/create/', views.create_store, name='create_store'),
    path('shops/<int:shop_id>/products/add/', views.add_product, name='add_product'),
    path('products/', views.all_products, name='all_products'),
    path('shops/<int:shop_id>/products/', views.product_list, name='product_list'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('store/<int:shop_id>/edit/', views.edit_store, name='edit_store'),
    path('store/<int:shop_id>/delete/', views.delete_store, name='delete_store'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset_form'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('homepage/', views.homepage, name='homepage'),
]
