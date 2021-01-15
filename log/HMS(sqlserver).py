import mysql.connector
from getpass import getpass
from mysql.connector import connect, Error
def exmany():
    insert_reviewers_query = """
INSERT INTO reviewers
(first_name, last_name)
VALUES ( %s, %s )
"""
    reviewers_records = [
        ("Chaitanya", "Baweja"),
        ("Mary", "Cooper"),
        ("John", "Wayne"),
        ("Thomas", "Stoneman"),
        ("Penny", "Hofstadter"),
        ("Mitchell", "Marsh"),
        ("Wyatt", "Skaggs"),
        ("Andre", "Veiga"),
        ("Sheldon", "Cooper"),
        ("Kimbra", "Masters"),
        ("Kat", "Dennings"),
        ("Bruce", "Wayne"),
        ("Domingo", "Cortes"),
        ("Rajesh", "Koothrappali"),
        ("Ben", "Glocker"),
        ("Mahinder", "Dhoni"),
        ("Akbar", "Khan"),
        ("Howard", "Wolowitz"),
        ("Pinkie", "Petit"),
        ("Gurkaran", "Singh"),
        ("Amy", "Farah Fowler"),
        ("Marlon", "Crafford"),
        ]
    with connection.cursor() as cursor:
        cursor.executemany(insert_reviewers_query, reviewers_records)
        connection.commit()
try:
    with connect(
        host="127.0.0.1",
        user=input("Enter username: "),
        password=getpass("Enter password: "),
        auth_plugin='mysql_native_password',
        database="online_movie_rating",
        ) as connection:
        db_init = """
CREATE DATABASE online_movie_rating;
CREATE TABLE movies(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    release_year YEAR(4),
    genre VARCHAR(100),
    collection_in_mil INT
);
CREATE TABLE reviewers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);
CREATE TABLE ratings (
    movie_id INT,
    reviewer_id INT,
    rating DECIMAL(2,1),
    FOREIGN KEY(movie_id) REFERENCES movies(id),
    FOREIGN KEY(reviewer_id) REFERENCES reviewers(id),
    PRIMARY KEY(movie_id, reviewer_id)
);
"""
        sh_table = "DESCRIBE movies"
        select = "SELECT * FROM movies LIMIT 5"
        insert = """
INSERT INTO movies (title, release_year, genre, collection_in_mil)
VALUES
("Forrest Gump", 1994, "Drama", 330.2)
"""
        
        with connection.cursor() as cursor:
            try:
                cursor.execute(insert)
                connection.commit()

                cursor.execute(select)
                result = cursor.fetchall()
                print("PRINT:"+str(result))
                for row in result:
                    print(row)
                exmany()
            except Error as e:
                connection.rollback()
                print(e)

except Error as e:
    print(e)

