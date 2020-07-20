import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime

# check for environment varialbe
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

startTime = datetime.datetime.now()
print(f"starting actions at:{startTime}")

f = open("books.csv")
reader = csv.reader(f)
i = 1
endtime = None
for isbn, title, author, year in reader:

    i += 1
    endtime = datetime.datetime.now()

    if title == "title":
        print("Skipping 1st row")
    else:
        db.execute("INSERT INTO public.books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {
            "isbn": isbn, "title": title, "author": author, "year": year})
        print(f"{i} book added successfully at {endtime}")

db.commit()
timeDiff = endtime - startTime
timeDiffSeconds = timeDiff.seconds
print(f"Total time to complete action: {timeDiff} ")
print(f"Total time to complete action in seconds: {timeDiffSeconds} ")
