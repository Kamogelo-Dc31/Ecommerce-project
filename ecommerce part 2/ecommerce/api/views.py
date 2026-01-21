from rest_framework import generics, permissions
from shop.models import Shop, Product, Review
from .serializers import ShopSerializer, ProductSerializer, ReviewSerializer

# Authentication required for creating/editing shops/products
class ShopCreateView(generics.CreateAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


# Read-only views
class VendorShopsList(generics.ListAPIView):
    serializer_class = ShopSerializer

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        return Shop.objects.filter(owner__id=vendor_id)


class ShopProductList(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        return Product.objects.filter(shop__id=shop_id)


class ProductReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product__id=product_id)
