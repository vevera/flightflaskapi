# Libraries
import psycopg2
import psycopg2.extras
import boto3 as aws
from werkzeug.security import check_password_hash, generate_password_hash



class FlightsSQL:
    """This class is responsible for connecting to the Database"""

    def __init__(self):

        self.conn = psycopg2.connect(
            # host="database-1.cyya4blmbzcp.us-east-1.rds.amazonaws.com",
            # user="postgres",
            # password="988991495",
            # dbname='postgres',
            # port=5432
            host="localhost",
            user="postgres",
            password="postgres",
            dbname="postgres",
            port=5432,
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def create_usr(self, user, password):
        try:
            self.cur.execute(
                "insert into user_creds(username, passwrd) values ('{}','{}')".format(
                    user, generate_password_hash(password, method="sha256")
                )
            )
            self.conn.commit()

        except Exception as error:
            print("User Registration Error: " + str(error))
            self.conn.rollback()
    def auth_user(self, username, password):
        try:
            self.cur.execute(
                "select * from user_creds where username = '{}'".format(username)
            )
            user = dict(self.cur.fetchone())
            if user:
                if check_password_hash(user["passwrd"], password):
                    print("Logged in successfully!\n")
                    self.cur.execute(
                        "select * from user_details where creds_id = {}".format(user["id"])
                    )
                    user_data = dict(self.cur.fetchone())
                    return {**user, **user_data}

            else:
                print("Wrong Username or Password! Please try again.\n")
                return None

        except (Exception, TypeError) as error:
            print("User does not exist: " + str(error))
            return None

    def user_details(self, firstname, lastname, adults, child, baby, email, creds_id):
        try:
            self.cur.execute(
                "insert into user_details(firstname, lastname, adults, child, baby, email,creds_id) values ('{}','{}',{},{},{},'{}',{})".format(
                    firstname, lastname, adults, child, baby, email, creds_id
                )
            )
            self.conn.commit()

        except Exception as error:
            print("City Insert Error: " + str(error))
            self.conn.rollback()

    def getting_user_data(self, user_id):

        try:
            self.cur.execute(
                "select * from user_details where creds_id = '{}'".format(user_id)
            )
            user = self.cur.fetchone()
            return user

        except Exception as error:
            print("Get Data Error: " + str(error))
            return None

    def getting_user(self, username):

        try:
            self.cur.execute(
                "select * from user_creds where username = '{}'".format(username)
            )
            user = self.cur.fetchone()
            return user

        except Exception as error:
            print("Get Data Error: " + str(error))
            return None

    def getting_data(self, table):
        try:
            self.cur.execute("select * from {}".format(table))
            data = self.cur.fetchall()
            return data

        except Exception as error:
            print("Get Data Error: " + str(error))
            return None

    def insert_city(self, iata, city):
        try:
            self.cur.execute(
                "insert into destination(iata, city) values ({},{})".format(iata, city)
            )
            self.conn.commit()

        except Exception as error:
            print("City Insert Error: " + str(error))

    def update_iata(self, iata, city):
        try:
            self.cur.execute(
                "UPDATE destination SET iata = {} WHERE city = {}".format(iata, city)
            )
            self.conn.commit()
            print(f"{city}'s IATA updated!")

        except Exception as error:
            print("IATA Update Error: " + str(error))

    def update_user(self, data):
        try:
            self.cur.execute(
                """ 
                UPDATE user_details
                SET firstname = '{}', 
                lastname = '{}', 
                email = '{}'
                WHERE creds_id = {};
                """.format(
                data.get("firstname"), 
                data.get("lastname"), 
                data.get("email"), 
                data.get("id")
            )
            )
            self.conn.commit()
            self.cur.execute(
                "select * from user_details as ud, user_creds as u where ud.creds_id = u.id and u.id = {}".format(data.get("id"))
            )
            user_data = dict(self.cur.fetchone())
            return user_data
        except Exception as error:
            print("IATA Update Error: " + str(error))
            return None

    def insert_details(
        self,
        date1,
        date2,
        cabin,
        seats,
        flight1,
        flight2,
        total_days,
        price,
        url,
        dest_id,
    ):
        try:

            seats = seats if seats is not None else "NULL"

            flights = (
                "insert into flights_details(departure_date, return_date, cabin, seats, departure_flight,"
                "return_flight, total_days, price, url, destination_id) "
                "values('{}','{}','{}',{},{},{},{},{},'{}',{})".format(
                    date1,
                    date2,
                    cabin,
                    seats,
                    flight1,
                    flight2,
                    total_days,
                    price,
                    url,
                    dest_id,
                )
            )

            self.cur.execute(flights)
            self.conn.commit()
            print("Flight details saved into the database")

        except Exception as error:
            print("Flight Insert Error: " + str(error))

    def update_season(self):
        try:
            season = self.cur.execute(
                "Update flights_details set season = CASE "
                "WHEN EXTRACT(MONTH from departure_date) < 3 THEN 'Winter' "
                "WHEN EXTRACT(MONTH from departure_date) = 3 THEN "
                "CASE WHEN EXTRACT(DAY from departure_date) <= 20 THEN 'Winter' ELSE "
                "'Transition to "
                "Spring' END "
                "WHEN EXTRACT(MONTH from departure_date) < 6 THEN 'Spring' "
                "WHEN EXTRACT(MONTH from departure_date) = 6 THEN "
                "CASE WHEN EXTRACT(DAY from departure_date) <= 20 THEN 'Spring' ELSE "
                "'Transition to "
                "Summer' END "
                "WHEN EXTRACT(MONTH from departure_date) < 9 THEN 'Summer' "
                "WHEN EXTRACT(MONTH from departure_date) = 9 THEN "
                "CASE WHEN EXTRACT(DAY from departure_date) <= 20 THEN 'Summer' ELSE "
                "'Transition to "
                "Autumn' END "
                "WHEN EXTRACT(MONTH from departure_date) < 12 THEN 'Autumn' "
                "WHEN EXTRACT(MONTH from departure_date) = 12 THEN "
                "CASE WHEN EXTRACT(DAY from departure_date) <= 20 THEN 'Autumn' ELSE "
                "'Transition to "
                "Winter' END "
                "END"
            )
            self.conn.commit()
            return season

        except Exception as error:
            print("Season Update Error: " + str(error))

    def close(self):
        try:
            self.cur.close()
            self.conn.close()

            print("Database connection is closed \n")

        except Exception as error:
            print(str(error))


class FlightNoSQL:
    class Dynamo:
        client = aws.resource("dynamodb")

        @staticmethod
        def create(attribute_economy_business, PartitionKey, SortKey):
            table = FlightNoSQL.Dynamo.client.create_table(
                TableName=f"{attribute_economy_business}",
                KeySchema=[
                    {"AttributeName": f"{PartitionKey}", "KeyType": "HASH"},
                    {"AttributeName": f"{SortKey}", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": f"{PartitionKey}", "AttributeType": "S"},
                    {"AttributeName": f"{SortKey}", "AttributeType": "S"},
                ],
                BillingMode="PROVISIONED",
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )

            print(
                f"Creating {attribute_economy_business} table... Please give a moment to access!"
            )
            table.wait_until_exists()
            print(
                "You have",
                table.item_count,
                f"items on {attribute_economy_business} table!",
            )

        @staticmethod
        def insert_values(
            TableName,
            search_id,
            origin,
            departure_flight,
            departure_date,
            destination,
            return_flight,
            return_date,
            total_days,
            seats,
            price,
            url,
        ):
            table = FlightNoSQL.Dynamo.client.Table(f"{TableName}")

            print(f"Updating {TableName}, please give a moment!")

            table.put_item(
                Item={
                    "Search_id": f"{search_id}",
                    "City_from": f"{origin}",
                    "Departure_flight": f"{departure_flight}",
                    "Departure_date": f"{departure_date}",
                    "City_to": f"{destination}",
                    "Return_flight": f"{return_flight}",
                    "Return_date": f"{return_date}",
                    "Total_days": f"{total_days}",
                    "Seat_remaining": f"{seats}",
                    "Price_total": f"{price}",
                    "Booking_url": f"{url}",
                }
            )
            print(f"{TableName} updated, the {search_id} item was insert!")

        @staticmethod
        def getting_table(TableName, search_id, destination):
            table = FlightNoSQL.Dynamo.client.Table(f"{TableName}")

            data = table.get_intem(
                key={"Search_id": f"{search_id}", "City_to": f"{destination}"}
            )

            item = data["Item"]
            print(item)

        @staticmethod
        def get_cheaper_flight(TableName):
            table = FlightNoSQL.Dynamo.client.Table(f"{TableName}")
            cheaper = table.get_intem(
                key={"Search_id": f"{search_id}", "City_to": f"{destination}"}
            )
            print(table)