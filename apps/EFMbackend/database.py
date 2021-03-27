from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = 'root'
DB_PASSWORD = 'admin'
DB_HOST='localhost'
DB_DATABASE='efm_schema'

#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:admin@localhost/seddb' 
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
#print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
