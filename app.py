from flask import Flask, request, make_response, jsonify
import json
from flask_cors import CORS
import base64
from databases import FlightsSQL
from storage import S3

flightsql = FlightsSQL()

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
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

    # image_64_decode = base64.b64decode(data["picture"])

    # S3.create_bucket(data['username'])
    # S3.upload_to_bucket("profile.jpeg", image_64_decode, f"{data['username']}.s3")

    flightsql.user_details(
                        data["firstName"],
                        data["lastName"],
                        data["adults"], 
                        data["children"], 
                        data["babies"], 
                        data["email"], 
                        user["id"])

    #f"{data['username']}.s3-profile.jpeg"
    
    return {"inserted": True}


@app.route("/login", methods = ["POST"])
def app_login():
    data = request.get_json()

    check_user = flightsql.auth_user(
        data['username'],
        data['password'],
    )
    
    if check_user is not None:
        check_user["inserted"] = True
        return check_user
        
    return {"inserted": False}
    


@app.route("/update", methods = ["POST"])
def update():
    data = request.get_json()

    user_data = flightsql.update_user(data)

    # if check_user is not None:
    #     return {"inserted": True}
    
    return user_data