
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql://postgres:postgres@localhost:5432/ecommerce_db"
engine = create_engine(db_url) #Help us to connect with the DB
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)