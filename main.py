from flask import Flask, Response
from flask import request
from flask_cors import CORS
import json
import mysql.connector
import os
import logging
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

logger = logging.getLogger()

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    error_dict = {
        'code': error.code,
        'description': error.description,
        'stack_trace': traceback.format_exc() 
    }
    log_msg = f"HTTPException {error_dict.code}, Description: {error_dict.description}, Stack trace: {error_dict.stack_trace}"
    logger.log(msg=log_msg)
    response = jsonify(error_dict)
    response.status_code = error.code
    return response

@app.route("/api/healthcheck")
def hello_world():
    return json.loads('{"Access-Control-Allow-Origin": "*", "status1": "ok"}')

@app.route("/api/movie/top_rented_movies")
def get_top_rented_movies():
    db = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        database="sakila"
        )
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

    db = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        database="sakila"
    )

    if title == "":
        return {}

    cursor = db.cursor(buffered=True)

    statement  = """
    SELECT 
        film.film_id,
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
    
    db = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        database="sakila"
    )

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

@app.route("/api/customer/search")
def search_customers():
    customer_id = request.args.get('customer_id', default="%", type = int)
    name = request.args.get('name', default="%", type=str)
    limit = request.args.get('limit', default=30, type = int)
    offset = request.args.get('offset', default=0, type = int)

    if name == "%":
        name = {}
        name["first_name"] = "%"
        name["last_name"] = "%"
    else:
        name_split = name.split(" ")
        name = {}
        if len(name) < 2:
            name["first_name"] = name_split[0]
            name["last_name"] = "%"
        else:
            name["first_name"] = name_split[0]
            name["last_name"] = name_split[1]

    statement = """
    SELECT 
	    customer.customer_id,
        customer.first_name,
        customer.last_name,
        customer.email,
        address.address,
        address.address2,
        address.postal_code,
        address.phone,
        city.city,
        country.country
    FROM customer
    JOIN  address
    ON address.address_id = customer.address_id
    JOIN city
    ON city.city_id = address.city_id
    JOIN country
    ON country.country_id = city.country_id
    WHERE 
        customer.customer_id LIKE "{}%"
        AND customer.first_name LIKE "{}%"
        AND customer.last_name LIKE "{}"
    ORDER BY customer_id ASC
    LIMIT {}
    OFFSET {};
    """.format(customer_id, name["first_name"], name["last_name"], limit, offset)

    cursor = db.cursor()
    cursor.execute(statement)

    customers = {"results": []}
    customers["Access-Control-Allow-Origin"] = '*'

    for row in cursor:
        temp_dict = dict(zip(cursor.column_names, row))
        customer = {"customer_id": temp_dict["customer_id"],
                    "name" : temp_dict["first_name"] + " " + temp_dict["last_name"],
                    "email" : temp_dict["email"],
                    "phone" : temp_dict["phone"],
                    "address" : temp_dict["address"] + ", " +temp_dict["city"] + ", " + temp_dict["postal_code"] + ", " + temp_dict["country"]
                    }
        customers["results"].append(customer)
        
    return customers

@app.route("/api/customer/customer_details")
def get_customer_details():
    customer_id = request.args.get("customer_id", default="", type = int)

    statement = """SELECT 
        customer.customer_id,
        customer.first_name,
        customer.last_name,
        customer.email,
        address.address,
        address.address2,
        address.postal_code,
        address.phone,
        city.city,
        country.country
    FROM customer
    JOIN  address
    ON address.address_id = customer.address_id
    JOIN city
    ON city.city_id = address.city_id
    JOIN country
    ON country.country_id = city.country_id
    WHERE customer.customer_id = {}
    ORDER BY customer_id ASC;""". format(customer_id)

    cursor = db.cursor(buffered=True)
    cursor.execute(statement)
    response = {}
    temp_dict = dict(zip(cursor.column_names, cursor.fetchone()))
    customer = {"Access-Control-Allow-Origin": '*',
                "customer_id": temp_dict["customer_id"],
                "name" : temp_dict["first_name"] + " " + temp_dict["last_name"],
                "email" : temp_dict["email"],
                "phone" : temp_dict["phone"],
                "address" : temp_dict["address"] + ", " +temp_dict["city"] + ", " + temp_dict["postal_code"] + ", " + temp_dict["country"]
                }
    
    response.update(customer)
    response["rented movies"] = []

    # get movies rented by customer
    statement = """SELECT film.title FROM film
JOIN inventory
ON inventory.film_id = film.film_id
JOIN rental
ON rental.inventory_id = inventory.inventory_id
JOIN customer
ON customer.customer_id = rental.customer_id
WHERE customer.customer_id = {};""".format(response["customer_id"])

    cursor.execute(statement)

    for row in cursor:
        response["rented movies"].append(row[0])

    return response

@app.route("/api/movie/rent_movie", methods=['POST'])
def rent_movie():
    if request.method == "OPTIONS":
        return {}
    data = json.loads(request.get_data())
    
    if(data["staff_id"] == "" or data["inventory_id"] == "" or data["customer_id"] == ""):
        return {"error": "Missing Information"}
    
    # data validated and verified in js
    data['inventory_id'] = 1
    statement = """INSERT INTO rental (rental_date, inventory_id, customer_id, return_date, staff_id)
VALUES( CURRENT_TIMESTAMP, {}, {}, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 DAY), {});""".format(data["inventory_id"], data["customer_id"], data["staff_id"])
    
    try:    
        cursor = db.cursor(buffered=True)
        cursor.execute(statement)
        db.commit()
        return {"status": 200}
    except mysql.connector.Error as error:
        return {"status": 404, "error": "{}".format(error)}

@app.route("/api/verify", methods=['GET'])
def verify():
    employee_username = request.args.get("employee_username", default="-1", type=str)
    customer_id = request.args.get("customer_id", default="-1", type=int)
    film_id = request.args.get("film_id", default="-1", type=int)

    employee_username_statement = """SELECT * FROM staff WHERE username='{}';""".format(employee_username)
    customer_id_statement = """SELECT * FROM customer WHERE customer_id={};""".format(customer_id)
    film_id_statement = """SELECT * FROM inventory JOIN film 
        ON film.film_id = inventory.film_id
        WHERE film.film_id = {}
        LIMIT 1;""".format(film_id)
    
    response = {}
    data_not_found_flag = False

    # check for customer id
    cursor = db.cursor(buffered=True)
    cursor.execute(customer_id_statement)
    if(cursor.rowcount == 0):
        data_not_found_flag = True
        response["customer_id"] = {"status": 404, "error": "Data not found"}
    
    # check film id
    cursor.execute(film_id_statement)
    if(cursor.rowcount == 0):
        if(not data_not_found_flag):
            data_not_found_flag = True
        response["film_id"] = {"status": 404, "error": "Data not found"}

    # check employee id
    cursor.execute(employee_username_statement)
    if(cursor.rowcount == 0):
        if(not data_not_found_flag):
            data_not_found_flag = True
        response["employee_username"] = {"status": 404, "error": "Data not found"}

    # response if input is not verified
    if(data_not_found_flag):
        response["status"] = 404
        return response
    else:
        temp_dict = dict(zip(cursor.column_names, cursor.fetchone()))
        return {"status": 200, "message": "Verified", "password_hash": temp_dict["password"], "staff_id": temp_dict["staff_id"]}
    
    

if __name__ == '__main__':
    db = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        database="sakila"
        )
    CORS(app, resources={r"/api/*": {"origins": "http://localhost"}})
    app.run(host='127.0.0.1', port=8080, debug=True)