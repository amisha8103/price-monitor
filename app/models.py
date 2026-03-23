from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    category = Column(String)
    source = Column(String)
    external_id = Column(String)

    product_url = Column(String)
    description = Column(String)
    image_url = Column(String)

    current_price = Column(Numeric)
    currency = Column(String)

    last_updated = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="unique_product"),
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Numeric)
    timestamp = Column(DateTime, default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True)
    usage_count = Column(Integer, default=0)