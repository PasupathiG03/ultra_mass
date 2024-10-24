from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


password = 'postgres'

encoded_password = urllib.parse.quote_plus(password)

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{encoded_password}@192.168.0.117:5432/eladb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import urllib.parse

# password = 'postgres'

# encoded_password = urllib.parse.quote_plus(password)

# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{encoded_password}@192.168.0.117:5432/check25"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()