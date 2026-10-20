from fastapi import FastAPI, Depends
from pydantic_models import Product
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "**Welcome to Cloud Cart 📦 🛒**"


products = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="A Laptop", price=999.99, quantity=30),
    Product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    Product(id=4, name="Table", description="A wodden table", price=199.99, quantity=20),
]

## Initialize DB Session

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()

    count = db.query(database_models.Product).count

    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))

        db.commit()

init_db()

### All APIs

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products

@app.get("/products/count")
def get_all_products(db: Session = Depends(get_db)):
    total_products = db.query(database_models.Product).count()
    return {"total_products": total_products}

@app.get("/product/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    # for product in products:
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product
    return "Product Not found"
        
@app.post("/product")
def add_product(product: Product , db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return f"Added the product {product}"

@app.put("/product/{id}")
def update_product(id: int, product: Product , db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db.commit()
        return "Product Updated Successfully"
    else:
        return f"Product not found with id: {id}"

@app.delete("/product")
def delete_product(id: int , db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product Deleted"
    else:
        return f"Product not found with id: {id}"



