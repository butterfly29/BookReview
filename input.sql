CREATE TABLE books
(
    id SERIAL NOT NULL,
    isbn varchar(100) NOT NULL,
    title varchar (100) NOT NULL,
    author varchar(100) NOT NULL,
    year integer NOT NULL,
    PRIMARY KEY (isbn)
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