from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, select, func
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.ext.declarative import DeclarativeMeta
from config import DATABASE_URL
from datetime import datetime
from dataclasses import dataclass

Base: DeclarativeMeta = declarative_base()

@dataclass
class Product:
    id: int
    name: str
    price: float
    image: str
    url: str
    store: str

class Store(Base):
    __tablename__ = "stores"
    store_id = Column(Integer, primary_key=True)
    store_name = Column(String, nullable=False)
    last_retrieved_on = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductDB(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    product_name = Column(String, nullable=False)
    product_url = Column(String)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    store = relationship("Store")

class ProductPrice(Base):
    __tablename__ = "product_prices"
    price_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    price = Column(Float, nullable=False)
    retrieved_on = Column(DateTime, default=datetime.utcnow)

engine = create_engine(DATABASE_URL)

def get_all_products():
    with Session(engine) as session:
        products = session.execute(
            select(ProductDB, Store.store_name, ProductPrice.price)
            .join(Store, ProductDB.store_id == Store.store_id)
            .outerjoin(ProductPrice, ProductDB.product_id == ProductPrice.product_id)
            .where(ProductDB.is_active == True)
        ).all()
        return [
            Product(
                id=p.ProductDB.product_id,
                name=p.ProductDB.product_name,
                price=p.price if p.price is not None else None,
                image=p.ProductDB.image_url,
                url=p.ProductDB.product_url,
                store=p.store_name
            )
            for p in products
        ]

def get_product_count_and_max_id():
    with Session(engine) as session:
        count = session.execute(select(func.count()).select_from(ProductDB).where(ProductDB.is_active == True)).scalar()
        max_id = session.execute(select(func.max(ProductDB.product_id)).where(ProductDB.is_active == True)).scalar()
        return count, max_id or 0

def get_new_products(last_max_id):
    with Session(engine) as session:
        products = session.execute(
            select(ProductDB, Store.store_name, ProductPrice.price)
            .join(Store, ProductDB.store_id == Store.store_id)
            .outerjoin(ProductPrice, ProductDB.product_id == ProductPrice.product_id)
            .where(ProductDB.is_active == True)
            .where(ProductDB.product_id > last_max_id)
        ).all()
        return [
            Product(
                id=p.ProductDB.product_id,
                name=p.ProductDB.product_name,
                price=p.price if p.price is not None else None,
                image=p.ProductDB.image_url,
                url=p.ProductDB.product_url,
                store=p.store_name
            )
            for p in products
        ]