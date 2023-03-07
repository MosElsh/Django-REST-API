from rest_framework.serializers import ModelSerializer
from .models import Product, Country

class ListedProductsSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ("prodID", "name", "price", "colour", "available", "new")

class DetailedProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ("__all__")

class ListedCountriesSerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ("__all__")