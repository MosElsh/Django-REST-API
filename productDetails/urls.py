from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "Home"),
    path("api/products/<str:sortType>/<str:field>", views.FieldSortedListedProductView.as_view(), name = "Field Sorted Products Data"),
    path("api/products/<str:sortType>/", views.emptyFieldSort, name = "Empty Field Sort Redirection"),
    path("api/products/", views.emptySort, name = "Empty Sort"),
    path("api/products/<str:sortType>/<str:field>/", views.removeEmptyFilter, name="Return From Empty Filter"),
    path("api/products/<str:sortType>/<str:field>/<str:filterData>", views.FilteredFieldSortedListedProductView.as_view(), name="Filtered And Field Sorted Products Data"),
    path("api/product/<str:id>", views.DetailedProductView.as_view(), name="Detailed Product Data"),
    path("api/countries", views.CountriesListView.as_view(), name="Name Ordered Countries List Data"),
    path("customers/<str:accessID>/<str:jwt>", views.store_customer_details, name="Store Customer Details"),
]