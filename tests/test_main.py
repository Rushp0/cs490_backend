from main import app
import json
from unittest import TestCase

top_actors_response = json.loads("""{
  "Access-Control-Allow-Origin": "*",
  "results": [
    {
      "Movies": 42,
      "actor_id": 107,
      "first_name": "GINA",
      "last_name": "DEGENERES"
    },
    {
      "Movies": 41,
      "actor_id": 102,
      "first_name": "WALTER",
      "last_name": "TORN"
    },
    {
      "Movies": 40,
      "actor_id": 198,
      "first_name": "MARY",
      "last_name": "KEITEL"
    },
    {
      "Movies": 39,
      "actor_id": 181,
      "first_name": "MATTHEW",
      "last_name": "CARREY"
    },
    {
      "Movies": 37,
      "actor_id": 23,
      "first_name": "SANDRA",
      "last_name": "KILMER"
    }
  ]
}""")

customer_details_response = json.loads("""{
  "Access-Control-Allow-Origin": "*",
  "address": "164 Koss street",
  "address2": "",
  "city": "piscataay",
  "country": "United States",
  "customer_id": 605,
  "district": "NJ",
  "email": "rushi.patel1@sakila.com",
  "first_name": "Rushi",
  "full_address": "164 Koss street, piscataay, 08854, United States",
  "last_name": "Patel",
  "phone": "1234567890",
  "postal_code": "08854",
  "rented movies": [
    "ACADEMY DINOSAUR",
    "CHEAPER CLYDE"
  ]
}""")

customer_search_response = json.loads("""{
  "Access-Control-Allow-Origin": "*",
  "results": [
    {
      "address": "519 Brescia Parkway, Madiun, 69504, Indonesia",
      "customer_id": 500,
      "email": "REGINALD.KINDER@sakilacustomer.org",
      "name": "REGINALD KINDER",
      "phone": "793996678771"
    }
  ]
}""")

customer_delete_response = json.loads("""{
    "status": 200
}""")

customer_add_response = json.loads("""{
    "status": 200
}""")

def test_top_actors():
    response = app.test_client().get("/api/actor/top_actors")
    response = response.get_json()
    TestCase().assertDictEqual(response, top_actors_response)

def test_customer_details():
    response = app.test_client().get("/api/customer/customer_details?customer_id=605")
    response = response.get_json()
    TestCase().assertDictEqual(response, customer_details_response)

def test_customer_search():
    response = app.test_client().get("/api/customer/search?customer_id=500")
    response = response.get_json()
    TestCase().assertDictEqual(response, customer_search_response)

def test_add_customer():
    response = app.test_client().post("/api/customer/add", json=json.loads("""{
    "first_name":"TEST",
    "last_name":"TEST",
    "email":"TEST.TEST@sakila.com",
    "phone":"1564567898",
    "address":"1111 MySakila Drive",
    "address2":"",
    "district":"Alberta",
    "postal_code":"",
    "city":"Lethbridge",
    "country":"Canada"
    }"""))
    response = response.get_json()
    TestCase().assertDictEqual(response, customer_add_response)

def test_customer_delete():
    response = app.test_client().delete("/api/customer/delete?customer_id=613")
    response = response.get_json()
    TestCase().assertDictEqual(response, customer_delete_response)