from flask import Flask
from flask import request
from flask_cors import CORS
import json
import mysql.connector
import os

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
    
    films = {"Access-Control-Allow-Origin": '*',"results": []}

    for row in cursor:
        films["results"].append(dict(zip(cursor.column_names, row)))
    return films

@app.route("/api/movie/movie_details")
def get_movie_details():
    title = request.args.get('film_id', default="", type = str)

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
    WHERE film.film_id = "{}";
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
    limit = request.args.get('limit', default=30, type = int)
    offset = request.args.get('offset', default=0, type = int)
    
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

    statement = """   
    SELECT DISTINCT
        film.film_id,
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
    AND category.name LIKE "{}%"
    LIMIT {}
    OFFSET {};
    """.format(title, actor["first_name"], actor["last_name"], genre, limit, offset)

    cursor = db.cursor()
    cursor.execute(statement)

    films = {"results": []}

    for row in cursor:
        films["results"].append(dict(zip(cursor.column_names, row)))
        
    films["Access-Control-Allow-Origin"] = '*'
    return films

@app.route("/api/actor/top_actors")
def top_actors():
    cursor = db.cursor()

    cursor.execute("""
    SELECT
	    actor.actor_id,
        actor.first_name,
        actor.last_name,
        COUNT(*) AS Movies
    FROM actor
    JOIN film_actor
    ON film_actor.actor_id = actor.actor_id
    JOIN film
    ON film_actor.film_id = film.film_id
    GROUP BY actor_id
    ORDER BY Movies DESC
    LIMIT 5;
    """)

    actors = {"Access-Control-Allow-Origin": '*',"results": []}
    for row in cursor:
        actors["results"].append(dict(zip(cursor.column_names, row)))
    
    return actors

@app.route("/api/actor/actor_details")
def get_actor_details():
    actor_name = request.args.get('actor', default="", type = str)

    if actor_name == "":
        return {}
    
    cursor = db.cursor(buffered=True)
    actor = {"first_name": actor_name.split(" ")[0], "last_name": actor_name.split(" ")[1]}
    response = {"Access-Control-Allow-Origin": '*'}

    get_actor_id = """SELECT
	    actor.actor_id,
        actor.first_name,
        actor.last_name
    FROM actor
    WHERE actor.first_name = '{}' AND actor.last_name = '{}';""".format(actor["first_name"], actor["last_name"])

    cursor.execute(get_actor_id)

    data = cursor.fetchone()
    columns = cursor.column_names

    response.update(dict(zip(columns, data)))

    get_num_movies = """
    SELECT
	    actor.actor_id,
	    actor.first_name,
	    actor.last_name,
	    COUNT(*) as 'movies'
    FROM actor
    JOIN film_actor
    ON film_actor.actor_id = actor.actor_id
    JOIN film
    ON film_actor.film_id = film.film_id
    WHERE film_actor.actor_id = {};""".format(response["actor_id"])

    cursor.execute(get_num_movies)
    data = cursor.fetchone()
    columns = cursor.column_names
    response.update(dict(zip(columns, data)))

    get_top_5_rented_movies = """
    SELECT
	    film.title,
        COUNT(payment.rental_id) as count
    FROM film
    JOIN inventory
    ON inventory.film_id = film.film_id
    JOIN rental
    ON rental.inventory_id = inventory.inventory_id
    JOIN payment
    ON payment.rental_id = rental.rental_id
    JOIN film_actor
    ON film_actor.film_id = film.film_id
    WHERE film_actor.actor_id = {}
    GROUP BY film.title
    ORDER BY count DESC
    LIMIT 5;""".format(response["actor_id"])

    cursor.execute(get_top_5_rented_movies)
    response["top movies"] = []
    for row in cursor:
        response["top movies"].append(dict(zip(cursor.column_names, row)))

    return response 


if __name__ == '__main__':
    db = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database="sakila"
    )
    CORS(app, resources={r"/api/*": {"origins": "http://localhost"}})
    app.run(host='127.0.0.1', port=8080, debug=True)