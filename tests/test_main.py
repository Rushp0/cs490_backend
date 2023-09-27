from main import app
import json
from unittest import TestCase

top_rented_movies_response = json.loads("""{
  "Access-Control-Allow-Origin": "*",
  "results": [
    {
      "count": 34,
      "film_id": 103,
      "title": "BUCKET BROTHERHOOD"
    },
    {
      "count": 33,
      "film_id": 738,
      "title": "ROCKETEER MOTHER"
    },
    {
      "count": 32,
      "film_id": 331,
      "title": "FORWARD TEMPLE"
    },
    {
      "count": 32,
      "film_id": 382,
      "title": "GRIT CLOCKWORK"
    },
    {
      "count": 32,
      "film_id": 489,
      "title": "JUGGLER HARDLY"
    }
  ]
}""")

movie_details_id1 = json.loads("""{
  "Access-Control-Allow-Origin": "*",
  "category": "Documentary",
  "description": "A Epic Drama of a Feminist And a Mad Scientist who must Battle a Teacher in The Canadian Rockies",
  "length": 86,
  "release_year": 2006,
  "title": "ACADEMY DINOSAUR"
}""")

penelope_guiness_response = json.loads("""{
  "Access-Control-Allow-Origin": "*",
  "actor_id": 1,
  "first_name": "PENELOPE",
  "last_name": "GUINESS",
  "movies": 19,
  "top movies": [
    {
      "count": 29,
      "title": "GLEAMING JAWBREAKER"
    },
    {
      "count": 26,
      "title": "WESTWARD SEABISCUIT"
    },
    {
      "count": 24,
      "title": "COLOR PHILADELPHIA"
    },
    {
      "count": 23,
      "title": "ACADEMY DINOSAUR"
    },
    {
      "count": 22,
      "title": "ANGELS LIFE"
    }
  ]
}""")

def test_healthcheck():
    response = app.test_client().get("/api/movie/movie_details?film_id=1")
    response = response.get_json()
    TestCase().assertDictEqual(response, movie_details_id1)

def test_top_rented_movies():
    response = app.test_client().get("/api/movie/top_rented_movies")
    response = response.get_json()
    TestCase().assertDictEqual(response, top_rented_movies_response)

def test_actor_details():
    response = app.test_client().get("""/api/actor/actor_details?actor=PENELOPE%20GUINESS""")
    response = response.get_json()
    TestCase().assertDictEqual(response, penelope_guiness_response)