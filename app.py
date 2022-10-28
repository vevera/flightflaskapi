from flask import Flask, request, make_response, jsonify
import json
from flask_cors import CORS
import base64
from databases import FlightsSQL
from storage import S3
from backend_complie import Back
from threading import Thread
from data import data

flightsql = FlightsSQL()

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    # S3.listing_bucket("teste")
    # S3.listing_files("asiatrip")
    # S3.url_from_file("asiatrip", "turtle.jpg")
    #S3.create_bucket("fabio.s3")
    return "<p>Welcome to Flight Search API!</p>"



@app.route("/signup", methods = ["POST"])
def app_signup():

    
    data = request.get_json()

    check_user = flightsql.getting_user(data['username'])
    if check_user is not None:
        return {"inserted": False}


    flightsql.create_usr(
        data['username'],
        data['password'],
    )
    user = flightsql.getting_user(data['username'])

    image_64_decode = base64.b64decode(data["picture"])

    S3.create_bucket(data['username'].lower())
    
    image_64_decode = base64.b64decode(data["picture"])
    S3.upload_to_bucket("profile.jpeg", image_64_decode, f"{data['username'].lower()}.s3")

    flightsql.user_details(
                        data["firstName"],
                        data["lastName"],
                        data["adults"], 
                        data["children"], 
                        data["babies"], 
                        data["email"], 
                        user["id"],
                        )

    #f"{data['username']}.s3-profile.jpeg"
    response = flightsql.auth_user(data['username'], data['password'])
    response["inserted"] = True
    response["pic"] = S3.url_from_file(f"{data['username'].lower()}.s3", "profile.jpeg")
    return response


@app.route("/login", methods = ["POST"])
def app_login():
    data = request.get_json()

    check_user = flightsql.auth_user(
        data['username'],
        data['password'],
    )
    
    if check_user is not None:
        check_user["inserted"] = True
        check_user["pic"] = S3.url_from_file(f"{data['username'].lower()}.s3", "profile.jpeg")
        return check_user
        
    return {"inserted": False}
    


@app.route("/update", methods = ["POST"])
def update():
    data = request.get_json()

    user_data = flightsql.update_user(data)

    if data["picture"] != "":
        image_64_decode = base64.b64decode(data["picture"])
        S3.upload_to_bucket("profile.jpeg", image_64_decode, f"{data['username'].lower()}.s3")

    user_data["pic"] = S3.url_from_file(f"{data['username'].lower()}.s3", "profile.jpeg")

    return user_data


@app.route("/search", methods = ["POST"])
def search():

    request_data = request.get_json()
    flight_data = data()

    data.username = request_data.get("username")
    data.email = request_data.get("email")
    data.city = request_data.get("city")
    data.adults = int(request_data.get("adults"))
    data.kids = int(request_data.get("kids"))
    data.baby = int(request_data.get("baby"))
    data.ECONOMY_PRICE_COMPARE = int(request_data.get("ECONOMY_PRICE_COMPARE"))
    data.BUSINESS_PRICE_COMPARE = int(request_data.get("BUSINESS_PRICE_COMPARE"))

    #Back().flight_deals(flight_data)
    Thread(target=Back().flight_deals, args=(flight_data,)).start()

    return {"user_data":123}