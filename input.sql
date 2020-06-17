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
    PRIMARY KEY(name)

);

CREATE TABLE reviews
(
    email VARCHAR NOT NULL,
    rating INTEGER NOT NULL,
    comment VARCHAR(1200) NOT NULL,
    isbn VARCHAR NOT NULL
);      