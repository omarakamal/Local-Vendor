import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from shop.models import Category, Product

User = get_user_model()

@pytest.mark.django_db
def test_register_login_me():
    c = APIClient()
    r = c.post("/api/auth/register/", {"username":"t1","email":"t1@e.com","password":"Test12345!"}, format="json")
    assert r.status_code == 201
    r = c.post("/api/auth/login/", {"username":"t1","password":"Test12345!"}, format="json")
    assert "access" in r.data and "refresh" in r.data
    token = r.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    r = c.get("/api/me/")
    assert r.status_code == 200
    assert r.data["username"] == "t1"

@pytest.mark.django_db
def test_catalog_list_and_filters():
    cat = Category.objects.create(name_en="Drinks")
    Product.objects.create(category=cat, name_en="Coffee", sku="S1", price_cents=3000, stock_qty=5)
    Product.objects.create(category=cat, name_en="Tea", sku="S2", price_cents=2000, stock_qty=0)
    c = APIClient()
    r = c.get("/api/products/?in_stock=1&sort=price_desc")
    assert r.status_code == 200
    names = [i["name_en"] for i in r.data["results"]]
    assert "Coffee" in names and "Tea" not in names

@pytest.mark.django_db
def test_cart_to_order_flow():
    # create user and product
    user = User.objects.create_user(username="u1", password="Test12345!")
    cat = Category.objects.create(name_en="Drinks")
    p = Product.objects.create(category=cat, name_en="Coffee", sku="S3", price_cents=3000, stock_qty=5)

    c = APIClient()
    r = c.post("/api/auth/login/", {"username":"u1","password":"Test12345!"}, format="json")
    token = r.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # empty cart
    r = c.get("/api/me/cart/")
    assert r.status_code == 200 and r.data["items"] == []

    # add item
    r = c.post("/api/me/cart/items/", {"product_id": p.id, "qty": 2}, format="json")
    assert r.status_code == 200
    assert r.data["items"][0]["qty"] == 2

    # checkout
    r = c.post("/api/checkout/session/", {"vat_rate": 10.0, "shipping_cents": 0}, format="json")
    assert r.status_code == 200
    assert r.data["subtotal_cents"] == 6000
    assert r.data["vat_amount_cents"] == 600
    assert r.data["total_cents"] == 6600

    # orders list
    r = c.get("/api/me/orders/")
    assert r.status_code == 200 and len(r.data) == 1
