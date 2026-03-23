from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

API_KEY = "beccc0d7-608b-44ce-b95a-f0629e9eebcc"


def headers():
    return {"api-key": API_KEY}


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
    res = client.get("/products/1", headers=headers())
    assert res.status_code == 200


# ✅ 6. Invalid product
def test_invalid_product():
    res = client.get("/products/999999", headers=headers())
    assert res.status_code == 200
    assert "error" in res.json()


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


# ✅ 9. Invalid API key
def test_invalid_api_key():
    res = client.get("/products", headers={"api-key": "wrong"})
    assert res.status_code == 401


# ✅ 10. Product history structure
def test_product_history():
    res = client.get("/products/1", headers=headers())
    data = res.json()
    assert "history" in data