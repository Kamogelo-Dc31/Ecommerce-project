from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('vendors/<int:vendor_id>/stores/', views.VendorShopsList.as_view(), name='vendor_shops'),
    path('shops/<int:shop_id>/products/', views.ShopProductList.as_view(), name='shop_products'),
    path('products/<int:product_id>/reviews/', views.ProductReviewList.as_view(), name='product_reviews'),
    path('shops/create/', views.ShopCreateView.as_view(), name='create_shop_api'),
    path('products/create/', views.ProductCreateView.as_view(), name='create_product_api'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
