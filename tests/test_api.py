import pytest
from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.models import PriceHistory, Product, User
from main import app

client = TestClient(app)

API_KEY = "test-api-key"
PRODUCT_ID = None


def headers():
    return {"api-key": API_KEY}


@pytest.fixture(scope="module", autouse=True)
def seed_data():
    global PRODUCT_ID

    db = SessionLocal()

    user = db.query(User).filter(User.api_key == API_KEY).first()
    if not user:
        user = User(api_key=API_KEY)
        db.add(user)
        db.commit()

    product = db.query(Product).filter(
        Product.source == "testsource",
        Product.external_id == "test-1"
    ).first()

    if not product:
        product = Product(
            name="Test Product",
            brand="Test Brand",
            category="Test Category",
            source="testsource",
            external_id="test-1",
            product_url="http://example.com/test",
            description="Test description",
            image_url="http://example.com/test.png",
            current_price=100.0,
            currency="USD"
        )
        db.add(product)
        db.commit()
        db.refresh(product)

    PRODUCT_ID = product.id

    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == PRODUCT_ID
    ).first()
    if not history:
        db.add(PriceHistory(product_id=PRODUCT_ID, price=product.current_price))
        db.commit()

    db.close()
    yield


# ✅ 1. Test root
def test_root():
    res = client.get("/")
    assert res.status_code == 200


# ✅ 2. Auth required
def test_auth_missing():
    res = client.get("/products")
    assert res.status_code == 401


# ✅ 3. Get products
def test_get_products():
    res = client.get("/products", headers=headers())
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ✅ 4. Filter products
def test_filter_products():
    res = client.get("/products?min_price=1000", headers=headers())
    assert res.status_code == 200


# ✅ 5. Get single product
def test_get_product():
    res = client.get(f"/products/{PRODUCT_ID}", headers=headers())
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == PRODUCT_ID
    assert "history" in data


# ✅ 6. Invalid product
def test_invalid_product():
    res = client.get("/products/999999", headers=headers())
    assert res.status_code == 404


# ✅ 7. Analytics
def test_analytics():
    res = client.get("/analytics", headers=headers())
    assert res.status_code == 200
    data = res.json()
    assert "total_products" in data


# ✅ 8. Price filter edge case
def test_price_filter_edge():
    res = client.get("/products?min_price=1000000", headers=headers())
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ✅ 9. Invalid API key
def test_invalid_api_key():
    res = client.get("/products", headers={"api-key": "wrong"})
    assert res.status_code == 401


# ✅ 10. Product history structure
def test_product_history():
    res = client.get(f"/products/{PRODUCT_ID}", headers=headers())
    data = res.json()
    assert "history" in data
    assert isinstance(data["history"], list)


def test_min_price_negative():
    res = client.get("/products?min_price=-1", headers=headers())
    assert res.status_code == 400


def test_max_price_negative():
    res = client.get("/products?max_price=-1", headers=headers())
    assert res.status_code == 400


def test_min_greater_than_max():
    res = client.get("/products?min_price=200&max_price=100", headers=headers())
    assert res.status_code == 400


def test_analytics_empty_source():
    res = client.get("/analytics?source= ", headers=headers())
    assert res.status_code == 400


def test_analytics_empty_category():
    res = client.get("/analytics?category= ", headers=headers())
    assert res.status_code == 400