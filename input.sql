CREATE TABLE books
(
    id SERIAL NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    isbn VARCHAR NOT NULL,
    PRIMARY KEY(isbn)
);

CREATE TABLE users
(
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    PRIMARY KEY(email)

);

CREATE TABLE reviews
(
    email varchar(100) NOT NULL,
    rating integer NOT NULL,
    comment varchar(1200) NOT NULL,
    isbn varchar(100) NOT NULL
);    