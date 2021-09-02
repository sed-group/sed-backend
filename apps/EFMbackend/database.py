from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DB_USER = 'root'
DB_PASSWORD = 'secret'
DB_HOST='localhost'
DB_DATABASE='efm_schema'

#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:admin@localhost/seddb' 
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
#print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=1, 
    max_overflow=0
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
@contextmanager
def get_connection():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()