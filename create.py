# create_table.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgresql://myuser:mypassword@localhost/postgres")

# Create the table
Base = Base = declarative_base()
Base.metadata.create_all(bind=engine)

print("Table created successfully.")
