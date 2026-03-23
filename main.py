from fastapi import FastAPI, Depends
from fastapi import Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Product
from app.models import PriceHistory

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Price Monitoring API is running"}



@app.get("/products")
def get_products(
    db: Session = Depends(get_db),
    source: str = None,
    min_price: float = None,
    max_price: float = None
):
    query = db.query(Product)

    if source:
        query = query.filter(Product.source == source)

    if min_price:
        query = query.filter(Product.current_price >= min_price)

    if max_price:
        query = query.filter(Product.current_price <= max_price)

    products = query.all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "price": float(p.current_price),
            "source": p.source
        }
        for p in products
    ]

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).all()

    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": float(product.current_price),
        "source": product.source,
        "history": [
            {
                "price": float(h.price),
                "timestamp": h.timestamp
            }
            for h in history
        ]
    }