from flask import Flask
from flask import request
from flask_cors import CORS
import json
import mysql.connector

app = Flask(__name__)

@app.route("/api/healthcheck")
def hello_world():
    return json.loads('{"status": "ok"}')

@app.route("/api/movie/top_rented_movies")
def get_top_rented_movies():

    cursor = db.cursor()
    cursor.execute("""
        SELECT
	        inventory.film_id,
            film.title,
	        COUNT(payment.rental_id) as count
        FROM payment
        JOIN rental
        ON rental.rental_id = payment.rental_id
        JOIN inventory
        ON inventory.inventory_id = rental.inventory_id
        join film
        ON film.film_id = inventory.film_id
        GROUP BY inventory.film_id
        ORDER BY count DESC
        LIMIT 5;
    """)
    
    films = {"results": []}

    for row in cursor:
        films["results"].append(dict(zip(cursor.column_names, row)))
    films["Access-Control-Allow-Origin"] = '*'
    return films

# MOVIE TITLE MUST BE ENCODED WITH SPACES AS %20
@app.route("/api/movie/movie_details")
def get_movie_details():
    title = request.args.get('title', default="", type = str)

    if title == "":
        return {}

    cursor = db.cursor(buffered=True)

    statement  = """
    SELECT 
	    film.title,
        film.release_year,
        film.description,
        film.length,
        category.name as category
    FROM
	    film
    JOIN film_category
    ON film.film_id = film_category.film_id
    JOIN category
    ON film_category.category_id = category.category_id
    WHERE film.title = "{}";
    """.format(title)

    print(statement)

    cursor.execute(statement)
    
    if cursor.rowcount < 1:
        return {}
    response = dict(zip(cursor.column_names, cursor.fetchone()))
    response["Access-Control-Allow-Origin"] = '*'
    return response

@app.route("/api/movie/search")
def search_movies():
    title = request.args.get('title', default="%", type = str)
    actor = request.args.get('actor', default="%", type = str)
    genre = request.args.get('genre', default="%", type = str)
    
    if actor == "%":
        actor = {}
        actor["first_name"] = "%"
        actor["last_name"] = "%"
    else:
        actor_split = actor.split(" ")
        actor = {}
        if len(actor) < 2:
            actor["first_name"] = actor_split[0]
            actor["last_name"] = "%"
        else:
            actor["first_name"] = actor_split[0]
            actor["last_name"] = actor_split[1]

    statement = """   SELECT DISTINCT
	    film.title,
        film.release_year,
        film.description,
        film.length,
        category.name as category,
        actor.first_name as 'first name',
        actor.last_name as 'last name'
    FROM
	    film
    JOIN film_category
    ON film.film_id = film_category.film_id
    JOIN category
    ON film_category.category_id = category.category_id
    JOIN film_actor
    ON	film_actor.film_id = film.film_id
    JOIN actor
    ON	film_actor.actor_id = actor.actor_id
    WHERE film.title LIKE "{}%"
    AND actor.first_name LIKE "{}%"
    AND actor.last_name LIKE "{}%"
    AND category.name LIKE "{}%";
    """.format(title, actor["first_name"], actor["last_name"], genre)

    cursor = db.cursor()
    cursor.execute(statement)

    films = {"results": []}

    for row in cursor:
        films["results"].append(dict(zip(cursor.column_names, row)))
        
    films["Access-Control-Allow-Origin"] = '*'
    return films

if __name__ == '__main__':
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="DB1017490!",
    database="sakila"
    )
    CORS(app, resources={r"/api/*": {"origins": "http://localhost"}})
    app.run(host='127.0.0.1', port=8080, debug=True)