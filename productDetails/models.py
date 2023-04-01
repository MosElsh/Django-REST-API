from django.db import models

class Product(models.Model):
    prodID = models.CharField(max_length=100, primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    colour = models.CharField(max_length=40, null=False)
    type = models.CharField(max_length=40, null=False)
    available = models.BooleanField(null=False)
    new = models.BooleanField(null=False)

class Country(models.Model):
    countryID = models.CharField(max_length=100, primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=100, null=False)

class Customer(models.Model):
    userID = models.CharField(max_length=100, primary_key=True, null=False)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField()

class Watchlist(models.Model):
    watchlist_referenceID = models.CharField(max_length=100, primary_key=True, null=False, blank=False)
    userID = models.ForeignKey(to=Customer, on_delete=models.CASCADE, null=False, blank=False, db_column="userID")
    prodID = models.ForeignKey(to=Product, on_delete=models.CASCADE, null=False, blank=False, db_column="prodID")

#needs work
"""
class Address(models.Model):
    addressID = models.CharField(max_length=100, primary_key=True, null=False, blank=False)
    fullAddressFormat = models.CharField(max_length=500, null=False)
    streetNumber = models.CharField(max_length=6, null=False)
    addressLine1 = models.CharField(max_length=500, null=False)
    addressLine2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=False)
    region = models.CharField(max_length=100, null=True)
    country = models.ForeignKey(to="Country", on_delete=models.DO_NOTHING)
    postalCode = models.CharField(max_length=50, null=False)
"""

#needs work
"""
class Order(models.Model):
    orderID = models.CharField(max_length=100, primary_key=True, null=False, blank=False)
    userID = models.ForeignKey(to="Customer", on_delete=models.DO_NOTHING)
    nameOnOrder = models.CharField(max_length=100, null=False)
    email = models.EmailField()
    subtotal = models.DecimalField(max_digits=7, decimal_places=2, null=False)

"""