import os
import json

from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import urllib3
import psycopg2
import requests
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask import Flask, request, session, render_template, flash, url_for, redirect
from flask_session import Session


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

# create "scoped session" that ensures different users interaction with database is kept separate
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def signin():
    if "name" in session:
        flash("Already Signed In")
        return redirect(url_for("home"))
    else:
        return render_template("login.html")


@app.route("/signin_validation", methods=["POST", "GET"])
def signin_validation():
    if request.method == "POST":
        # get user info from input
        email = request.form["signinEmail"]
        password = request.form["signinPassword"]

        # check if password match with database
        check_user = db.execute("select * from public.users where email = :email", {
            "email": email}).fetchone()

        if check_user:
            list = []
            for i in check_user:
                list.append(i)

            check_name = list[0]
            check_email = list[1]
            check_pass = list[2]
            if check_email == email and check_pass == password:
                session.permanent = True
                session["name"] = check_name
                session["password"] = check_pass
                session["email"] = check_email
                flash("Login successful")
                return redirect(url_for("home"))

            else:
                flash("Username or Password is incorrect")
                return redirect(url_for("signin"))

        else:
            flash("You are not a registed user. Please register first.")
            return redirect(url_for("signin"))
    else:
        flash("Login failed")
        return redirect(url_for("signin"))


@app.route("/home")
def home():
    if 'email' in session:
        email = session['email']
        db_user_query = db.execute(
            "select * from public.users where email = :email", {'email': email}).fetchall()
        db_review_query = db.execute(
            " select * from public.reviews where email = :email", {'email': email}).fetchall()
        # root = request.url_root()
        userInfo = {
            'name': db_user_query[0][0],
            'email': session['email'],
            'password': db_user_query[0][2],
        }
        reviewCount = len(db_review_query)

        return render_template('index.html', userInfo=userInfo, reviewedbooks=db_review_query, reviewCount=reviewCount)
    else:
        flash("Login first")
        return redirect(url_for("signin"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # get info from user input
        name = request.form["signupName"]
        email = request.form["signupEmail"]
        password = request.form["signupPassword"]
        # check if email is already in table
        check_user = db.execute(
            "select * from public.users where email = :email", {'email': email}).fetchall()

        if check_user:
            flash("You are already registered.")
            return redirect(url_for("signin"))
        else:
            # add new user in database
            db.execute("INSERT INTO public.users (name, email, password) VALUES (:name, :email , :password)", {
                "name": name, "email": email, "password": password})
            db.commit()

            # save the data in session
            session["name"] = name
            session["email"] = email
            session["password"] = password

            flash("Registration successful")
            return redirect(url_for("home"))
    else:
        if "name" in session:
            flash("You are already registered")
            return redirect(url_for("home"))
        else:
            return render_template("login.html")


@app.route("/signout")
def signout():
    if "name" in session:
        session.pop("name", None)
        session.pop("email", None)
        session.pop("pasword", None)

        flash("Signed out successfully")
        return redirect(url_for("signin"))
    else:
        flash("Already Signed out")
        return redirect(url_for("signin"))


@app.route('/book', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        title = request.form['byTitle']
        title = title.title()
        author = request.form['byAuthor']
        year = request.form['byYear']
        isbn = request.form['byIsbn']

        list = []
        text = None
        baseUrl = request.base_url
        if title:
            result = db.execute(
                " SELECT * FROM books WHERE title LIKE '%"+title+"%' ;").fetchall()
            text = title
        elif author:
            result = db.execute(
                " SELECT * FROM books WHERE author LIKE '%"+author+"%' ;").fetchall()
            text = author
        elif year:
            result = db.execute(
                " SELECT * FROM books WHERE year = :year", {'year': year}).fetchall()
            text = year
        else:
            result = db.execute(
                " SELECT * FROM books WHERE isbn LIKE '%"+isbn+"%' ;").fetchall()
            text = isbn

        # if found then save it in list
        if result:
            for i in result:
                list.append(i)
            itemsCount = len(list)
            return render_template('search.html', baseUrl=baseUrl,  items=list, msg="Yei ! Search result found", text=text, itemsCount=itemsCount)

        # if not found show a not found message
        else:
            return render_template('search.html', msgNo="Sorry! No books found", text=text)

    return render_template('search.html')


@app.route('/book/<string:isbn>', methods=['GET', 'POST'])
def singleBook(isbn):

    isbn = isbn
    email = session['email']

    apiCall = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "qijKUt0YAQZ7izbpOTJQg", "isbns": isbn})
    apidata = apiCall.json()
    dbdata = db.execute(
        " SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    dbreviews = db.execute(
        'SELECT * FROM reviews WHERE isbn = :isbn', {'isbn': isbn}).fetchall()

    alreadyHasReview = db.execute(
        'SELECT * FROM public.reviews WHERE isbn = :isbn and email = :email ', {'isbn': isbn, 'email': email}).fetchall()
    if request.method == 'POST':
        if alreadyHasReview:
            flash('You alreaddy submitted a review on this book')
        else:
            rating = int(request.form['rating'])
            comment = request.form['comment']
            email = session['email']
            fisbn = request.form['isbn']
            db.execute("INSERT into public.reviews (email, rating, comment, isbn) Values (:email, :rating, :comment, :isbn)", {
                       'email': email, 'rating': rating, 'comment': comment, 'isbn': fisbn})
            db.commit()
            flash('Awesome, Your review added successfully ')

    if apiCall:
        return render_template('book.html', apidata=apidata, dbdata=dbdata, dbreviews=dbreviews, isbn=isbn)
    else:
        flash('Data fetch failed')
        return render_template('book.html')


@app.route("/book/api/<string:isbn>")
def api(isbn):
    if 'email' in session:
        data = db.execute(
            "SELECT * FROM public.books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if data == None:
            return render_template('404.html')
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "qijKUt0YAQZ7izbpOTJQg", "isbns": isbn})
        average_rating = res.json()['books'][0]['average_rating']
        work_ratings_count = res.json()['books'][0]['work_ratings_count']
        x = {
            "title": data.title,
            "author": data.author,
            "year": data.year,
            "isbn": isbn,
            "review_count": work_ratings_count,
            "average_rating": average_rating
        }
        # api=json.dumps(x)
        # return render_template("api.json",api=api)
        return jsonify(x)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
