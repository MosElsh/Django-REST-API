from django.test import TestCase
from django.test.client import Client
from .models import Customer, Watchlist, Product, Country
from uuid import uuid4



class CustomerTests(TestCase):
    def test_view_codes(self):
        c = Client()
        res = c.get("/customers/hvfsdvfg/svdashvcgdahsgcd", follow=True) # Should work but returns nothing.
        self.assertEqual(res.status_code, 200)



class CountryTests(TestCase):
    def test_view_codes(self):
        c = Client()
        res = c.get("/api/countries", follow=True)
        self.assertEqual(res.status_code, 200)

    def test_data_retrieval(self):
        countries = Country.objects.all().values()
        self.assertEqual(len(countries), 1)







class ProductsTests(TestCase):
    def test_view_codes(self):
        c = Client()
        res = c.get("/api/products/asc/prodID", follow=True)
        self.assertEqual(res.status_code, 200)
        
        res = c.get("/api/products/", follow=True)
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/products/asc", follow=True)
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/products/asc/price", follow=True)
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/products/desc/prodID", follow=True)
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/products/desc/price", follow=True)
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/products/desc", follow=True)
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/product/djhasvdghsavhgdsahvd", follow=True) # Should work but returns nothing.
        self.assertEqual(res.status_code, 200)

    def test_data_retrieval(self):

        # All Products Ascending Relevance
        self.assertEqual(len(Product.objects.all().order_by("prodID").values()), 17)

        data = list(Product.objects.all().order_by("prodID").values_list())
        self.assertListEqual(data, sorted(data, key=lambda data:data[0]))

        # All Products Ascending Price
        data = list(Product.objects.all().order_by("price").values_list())
        self.assertListEqual(data, sorted(data, key=lambda data:data[3], reverse=False))

        # All Products Descending Price
        data = list(Product.objects.all().order_by("price").reverse().values_list())
        self.assertListEqual(data, sorted(data, key=lambda data:data[3], reverse=True))

        # Test Clothes Type Formal
        data = Product.objects.filter(type="Formal").values()
        self.assertEqual(len(data), 4)

        # Test Clothes Type Polo Shirts
        data = Product.objects.filter(type="Polo Shirts").values()
        self.assertEqual(len(data), 1)

        # Test Clothes Type Shirts
        data = Product.objects.filter(type="Shirts").values()
        self.assertEqual(len(data), 12)

        # Test Clothes Type New
        data = Product.objects.filter(new=True).values()
        self.assertEqual(len(data), 5)

        # Test Available Clothes Only
        data = Product.objects.filter(available=True).values()
        self.assertEqual(len(data), 13)

        # Test Each Product ID returns that product's information
        all_product_ids = [ id_list[0] for id_list in Product.objects.all().values_list("prodID")]
        for id in all_product_ids:
            self.assertEqual(len(Product.objects.filter(prodID=id)), 1)








class WatchlistTests(TestCase):
    def test_view_codes(self):
        c = Client()

        res = c.get("/api/watchlist/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1vc2Vsc2gxIn0.DwTZEakYCDTfqA7nQgFkWVUWv22KMTzP_HCyy8rA9ds/get", follow=True) # Should work but returns nothing.
        self.assertEqual(res.status_code, 200)

        res = c.get("/api/watchlist/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1vc2Vsc2gxIn0.DwTZEakYCDTfqA7nQgFkWVUWv22KMTzP_HCyy8rA9ds", follow=True) # Should work but returns nothing.
        self.assertEqual(res.status_code, 200)

    def test_data_retrieval(self):
        userID = Customer.objects.filter(name="M E").values("userID")[0]['userID']
        user_watchlist = Watchlist.objects.filter(userID=userID).values()
        self.assertEqual(len(user_watchlist) > 0, True)

    def test_data_addition(self):
        userID = Customer.objects.filter(name="M E")
        all_products = [ product for product in Product.objects.all()]
        for product in all_products:
            Watchlist(watchlist_referenceID=str(uuid4()), userID=userID[0], prodID=product).save()

        self.assertEqual(len(Watchlist.objects.all().values("watchlist_referenceID").values()), 18) # 17 + 1 where there's the original product in the product database.

    def test_data_removal(self):
        userID = Customer.objects.filter(name="M E")
        all_products = [ product for product in Product.objects.all()]
        for product in all_products:
            Watchlist(watchlist_referenceID=str(uuid4()), userID=userID[0], prodID=product).save()

        # Removes all values, should become 0.
        for product in all_products:
            Watchlist.objects.filter(userID=userID[0], prodID=product).delete()

        self.assertEqual(len(Watchlist.objects.all().values()), 0)