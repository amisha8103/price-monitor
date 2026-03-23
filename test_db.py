from app.db import SessionLocal
from app.models import Product, PriceHistory

db = SessionLocal()

# Create product
product = Product(
    name="Test Chanel Belt",
    brand="Chanel",
    category="Accessories",
    source="1stdibs",
    external_id="test123",
    product_url="https://example.com",
    description="Test product",
    image_url="https://image.com",
    current_price=2500,
    currency="USD"
)

db.add(product)
db.commit()
db.refresh(product)

# Add price history
history = PriceHistory(
    product_id=product.id,
    price=2500
)

db.add(history)
db.commit()

print("Inserted successfully!")