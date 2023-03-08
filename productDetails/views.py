from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from rest_framework.views import APIView
from .models import Product, Customer, Country
from .serializers import ListedProductsSerializer, DetailedProductSerializer, ListedCountriesSerializer
from uuid import uuid4
import os, dotenv
from jwt import decode

class DetailedProductView(APIView):

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        product = Product.objects.filter(prodID=id)
        serializer = DetailedProductSerializer(product, many=True)
        return JsonResponse(serializer.data, safe=False)


class FieldSortedListedProductView(APIView):

    def get(self, request, *args, **kwargs):
        field = kwargs['field']
        sortType = kwargs['sortType']

        # Check that all the data is valid.
        if not (validateSortType(sortType) and validateFieldEntered(field, Product)):
            return JsonResponse({}, safe=False)
        
        allProducts = Product.objects.all().order_by(field)
        
        if sortType == "desc":
            allProducts = allProducts.reverse()

        serializer = ListedProductsSerializer(allProducts, many=True)
        return JsonResponse(serializer.data, safe=False)

class FilteredFieldSortedListedProductView(APIView):

    def get(self, request, *args, **kwargs):
        field = kwargs['field']
        sortType = kwargs['sortType']
        filterData = kwargs['filterData']

        # Check that all the data is valid.
        if not (validateSortType(sortType) and validateFieldEntered(field, Product)) or filterData == "":
            return JsonResponse({}, safe=False)

        # Remove the last character if there's an & character for better processing of filters.
        if filterData[-1] == "&":
            filterData = filterData[0:-1]

        # Split filter data by the & and iterate through the list to process the filters.
        filtersList = []
        splitFilterData = filterData.split("&")

        # Colours will have their own set of filter parameters as they need an OR operator.
        colourQueries = Q()

        # Process filter data.
        for filter in splitFilterData:
            filterName, filterValues = filter.split("=")
            if filterName == "price":
                minPrice, maxPrice = filterValues.split(",")

                priceFilterObjects = {}
                priceFilterObjects[filterName + "__gte"] = minPrice
                filtersList.append(priceFilterObjects)

                priceFilterObjects = {}
                priceFilterObjects[filterName + "__lte"] = maxPrice
                filtersList.append(priceFilterObjects)

            elif filterName == "colour":
                coloursList = filterValues.split("|")
                for colour in coloursList:
                    colourQueries = colourQueries | Q(colour=str(colour).title())

            elif filterName == "available":
                filtersList.append({"available": True if filterValues == "Yes" else False})

            elif filterName == "type":
                filtersList.append({"type": filterValues})

            elif filterName == "new":
                filtersList.append({"new": True if filterValues == "Yes" else False})

        # Return data after applying normal filters (price, available, type, new).
        filteredProducts = Product.objects.all()
        for filter in filtersList:
            filteredProducts = filteredProducts.filter(**filter)

        # If colour filters aren't empty, apply them too.
        if colourQueries != Q():
            filteredProducts = filteredProducts.filter(colourQueries)

        filteredProducts = filteredProducts.order_by(field)

        if sortType == "desc":
            filteredProducts = filteredProducts.reverse()

        serializer = ListedProductsSerializer(filteredProducts, many=True)
        return JsonResponse(serializer.data, safe=False)

class CountriesListView(APIView):

    def get(self, request, *args, **kwargs):
        countries = Country.objects.all().order_by("name")
        serializer = ListedCountriesSerializer(countries, many=True)
        return JsonResponse(serializer.data, safe=False)

def store_customer_details(request, accessID, jwt):

    # Check accessID is correct. If not, don't continue.
    if accessID != os.environ['CUSTOMER_MODEL_URL_ACCESS']:
        return JsonResponse({})

    # Decode data from JWT and get the email separately. keep the dictionary as it may be needed later.
    decodedData = decode(jwt, os.environ['JWT_SECRET'], algorithms=['HS256'])
    email = decodedData['email']

    # If not a registered user, use the dicitionary to add an ID and create a new customer.
    if (len(Customer.objects.filter(email=email))) == 0:
        decodedData['userID'] = str(uuid4())
        newCustomer = Customer(**decodedData)
        newCustomer.save()

    return JsonResponse({})

def home(request):
    return HttpResponseRedirect("api/products/asc/prodID")

def emptySort(request):
    return HttpResponseRedirect(request.get_full_path() + "asc")

def emptyFieldSort(request, sortType):
    return HttpResponseRedirect(request.get_full_path() + "prodID")

def removeEmptyFilter(request, sortType, field):
    return HttpResponseRedirect(str(request.get_full_path())[0:-1])


""" Not part of URLs are the functions below. """

def validateFieldEntered(field, model):
    availableFields = [field.name for field in model._meta.get_fields()]
    if field in availableFields:
        return True
    return False

def validateSortType(sortType):
    if sortType == "asc" or sortType == "desc":
        return True
    return False