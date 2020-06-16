import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# check for environment varialbe
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)
for title, author, years, isbn in reader:

    db.execute("INSERT INTO books (Title, Author, Years, ISBN) VALUES (:Title, :Author, :Years, :ISBN)", {
               "Title": title, "Author": author, "Years": years, "ISBN": isbn})
    print(f"Added book {title} by {author} to database.")

db.commit()
