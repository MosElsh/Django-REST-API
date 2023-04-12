from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from rest_framework.views import APIView
from .models import Product, Customer, Country, Watchlist
from .serializers import ListedProductsSerializer, DetailedProductSerializer, ListedCountriesSerializer
from uuid import uuid4
import os
from jwt import decode

class DetailedProductView(APIView):
    """ Display the full product information for one product only. """

    def get(self, request, *args, **kwargs):
        """ Display the full product information for one product only. """

        id = kwargs['id']
        product = Product.objects.filter(prodID=id)
        serializer = DetailedProductSerializer(product, many=True)
        return JsonResponse(serializer.data, safe=False)


class FieldSortedListedProductView(APIView):
    """ Display the list of products sorted upon the user's choice. """

    def get(self, request, *args, **kwargs):
        """ Display the list of products sorted upon the user's choice. """

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
    """ Display the list of chosen, filtered products sorted upon the user's choice. """

    def get(self, request, *args, **kwargs):
        """ Display the list of chosen, filtered products sorted upon the user's choice. """

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
    """ Display the list of countries available. """

    def get(self, request, *args, **kwargs):
        """ Display the list of countries available. """

        countries = Country.objects.all().order_by("name")
        serializer = ListedCountriesSerializer(countries, many=True)
        return JsonResponse(serializer.data, safe=False)

def store_customer_details(request, accessID, jwt):
    """ Store the customer's new details. Updates the name of a returning user if needed. """

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

    # Check to see that the user's name is up to date. If not, update the user with that new name.
    user_name_old = Customer.objects.filter(email=email).values_list("name")[0][0]
    if user_name_old != decodedData['name']:
        Customer.objects.filter(email=email).update(name=decodedData['name'])

    return JsonResponse({})



def get_watchlist_products(request, jwt):
    """ Returns the list products that were starred by the user. """

    # Get the user ID using the email.
    email = decode(jwt, os.environ['JWT_SECRET'], algorithms=['HS256'])['email']
    customers = Customer.objects.filter(email=email).values()
    if len(customers) == 0:
        return JsonResponse({}, safe=False)
    userID = customers[0]['userID']

    # Return the user's watchlist.
    watchlist_data = []
    products = Product.objects.all()
    for product in products:
        watchlist_reference = product.watchlist_set.filter(userID=userID).values()
        if len(watchlist_reference) == 1:
            watchlist_data.append([list(Product.objects.filter(prodID=watchlist_reference[0]['prodID_id']).values())[0], watchlist_reference[0]])

    return JsonResponse(watchlist_data, safe=False)








def process_watchlist_change(request, jwt):
    """ Adds or removes products from the user's watchlist. """

    decoded_data = decode(jwt, os.environ['JWT_SECRET'], algorithms=['HS256'])
    email = decoded_data['email']

    # Get the user ID using the email.
    customers = Customer.objects.filter(email=email).values()
    if len(customers) == 0:
        return JsonResponse({}, safe=False)
    userID = customers[0]['userID']

    prodID = decoded_data['prodID']
    process = decoded_data['process']

    # Process watchlist changes by adding or removing a product from the watchlist.
    if process == "add":
        watchlist_referenceID = str(uuid4())

        if len(Product.objects.filter(prodID=prodID)) != 1:
            return JsonResponse({}, safe=False)

        Watchlist(watchlist_referenceID=watchlist_referenceID, prodID=Product.objects.get(prodID=prodID), userID=Customer.objects.get(userID=userID)).save()
    elif process == "remove":
        Watchlist.objects.filter(prodID=prodID, userID=userID).delete()

    return JsonResponse(["Done"], safe=False)








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