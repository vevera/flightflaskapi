# Libraries
from search import FlightSearch
from alert import FlightAlert
from databases import FlightsSQL, FlightNoSQL
from datetime import datetime, timedelta
import pyshorteners

# Instances
fs = FlightSearch()
fa = FlightAlert()
fdb = FlightsSQL()
fdyn = FlightNoSQL()

# Date
tomorrow = datetime.now() + timedelta(days=1)
two_years_from_tomorrow = tomorrow + timedelta(days=(24 * 30))

begin_date = tomorrow.date()
end_date = two_years_from_tomorrow.date()
cabin = 'C'
cabin_name = {'F': 'First Class', 'C': 'Business', 'W': ' Premium Economy', 'M': 'Economy'}

# Set up Script
username = None
email = None

origin_city = None
origin_code = None

adults = None
kids = None
baby = None

# Setting up the Search Prices
ECONOMY_PRICE_COMPARE: int = 0
BUSINESS_PRICE_COMPARE: int = 0

# Getting Routes Values from the Database
routes = fdb.getting_data('destination')


# Return Messages Methods
def send_alert(attribute_economy_business, short_url, dest_code):
    """
    This method is responsible for mount the Email layout.

    :param email:
    :param dest_code: Airport Code of the Destination City
    :param short_url: A short version of the booking url
    :param attribute_economy_business: Flight Cabin Status
    :return: A Email layout with all the important details about the flight.
    """

    message = f"\nPrice: {attribute_economy_business.price} R$"
    message += f"\nAdult Fare: {attribute_economy_business.adults_fare} R$"
    message += f"\nKid Fare: {attribute_economy_business.kids_fare} R$"
    message += f"\nBaby Fare: {attribute_economy_business.infants_fare} R$"
    message += f"\nSeats Left: {attribute_economy_business.seat}"
    message += f"\nAirline: {attribute_economy_business.airline}"
    message += f"\nTotal of Days: {attribute_economy_business.total_days}"
    message += f"\nBooking: {short_url}"
    message += f"\n"
    message += f"\nFlight Details"
    message += f"\n"
    message += f"\nDeparture :"
    message += f"\nOrigin: {attribute_economy_business.origin_city} - " \
               f"{attribute_economy_business.origin_airport}"
    message += f"\nDate: {attribute_economy_business.departure_date}"
    message += f"\nTime: {attribute_economy_business.departure_time}"
    message += f"\nFlight Number: {attribute_economy_business.departure_number}"
    message += f"\nAirplane: {attribute_economy_business.airplane_departure}"
    message += f"\n"
    message += f"\nReturn :"
    message += f"\nOrigin: {attribute_economy_business.destination_city} - " \
               f"{attribute_economy_business.destination_airport}"
    message += f"\nDate: {attribute_economy_business.return_date}"
    message += f"\nTime: {attribute_economy_business.return_time}"
    message += f"\nFlight Number: {attribute_economy_business.return_number}"
    message += f"\nAirplane: {attribute_economy_business.airplane_return}"

    fa.send_alert(str.upper(
        f"Low price alert!!!! {origin_code} - {dest_code} "
        f"(Class : {cabin_name[attribute_economy_business.cabin_departure]})"), message, email)


def terminal_return(attribute_economy_business, origin, dest, price):
    """
    This method is responsible for a terminal return.

    :param attribute_economy_business: Flight Cabin Status.
    :param origin: Departure City.
    :param dest: Destination City.
    :param price: Total price.
    :return: A compiled text about the flight
    """
    print(f'{cabin_name[attribute_economy_business.cabin_departure]} Flight Found'
          f"\nLow price alert!!!! {origin} - {dest} "
          f"\nPrice: {price} R$")


class Back:

    # Main Loop
    @staticmethod
    def flight_deals(data):
        """
        This method is responsible for getting the cheapest flight every hour.

        :return: A compiled list of the flights.
        """

        # Globals
        global username
        username = data.username

        global email
        email = data.email

        global origin_city
        origin_city = str.title(f"{data.city}")

        global origin_code
        origin_code = fs.location_code(f"{origin_city}")

        global adults
        adults = data.adults

        global kids
        kids = data.kids

        global baby
        baby = data.baby

        global ECONOMY_PRICE_COMPARE
        ECONOMY_PRICE_COMPARE = data.ECONOMY_PRICE_COMPARE

        global BUSINESS_PRICE_COMPARE
        BUSINESS_PRICE_COMPARE = data.BUSINESS_PRICE_COMPARE

        while isinstance(routes, type(None)) is False:

            for city in routes:
                dest_city = city['city']
                dest_code = city['iata']
                dest_id = city['id']

                print(f'Searching {dest_city}!!!\n')
                business = fs.flights(origin_code,
                                      dest_code,
                                      begin_date,
                                      end_date,
                                      adults,
                                      kids,
                                      baby,
                                      cabin
                                      )
                economy = fs.flights(origin_code,
                                     dest_code,
                                     begin_date,
                                     end_date,
                                     adults,
                                     kids,
                                     baby,
                                     None
                                     )

                # URL Shortener Object
                shortener = pyshorteners.Shortener()

                try:
                    if business.price < BUSINESS_PRICE_COMPARE:

                        # URL
                        short_url = shortener.tinyurl.short(business.url)

                        # Terminal Return
                        terminal_return(business, origin_code, dest_code, business.price)

                        # Insert Flight Details on a SQL Table
                        # fdb.insert_details(business.departure_date, business.return_date,
                        #                    cabin_name[business.cabin_departure], business.seat, business.departure_number,
                        #                    business.return_number, business.total_days, business.price, short_url, dest_id)
                        #
                        # fdb.update_season()

                        # Insert Dynamo Table Items
                        fdyn.Dynamo.insert_values("business", business.search_id, origin_city, business.departure_number, business.departure_date,
                                                  dest_city, business.return_number, business.return_date, business.total_days,
                                                  business.seat, business.price, short_url)

                        print("Dynamo Table Updated")

                        # Email Message
                        send_alert(business, short_url, dest_code)
                        print('Text/Email sent\n')

                    elif economy.price < ECONOMY_PRICE_COMPARE:

                        # URL
                        short_url = shortener.tinyurl.short(economy.url)

                        # Terminal Return
                        terminal_return(economy, origin_code, dest_code, economy.price)

                        # # Insert Flight Details on a SQL Table
                        # fdb.insert_details(economy.departure_date, economy.return_date,
                        #                    cabin_name[business.cabin_departure], economy.seat, economy.departure_number,
                        #                    economy.return_number, economy.total_days, economy.price, short_url, dest_id)
                        #
                        # fdb.update_season()

                        # Insert Dynamo Table Items
                        fdyn.Dynamo.insert_values("economy", economy.search_id, origin_city, economy.departure_number, economy.departure_date,
                                                  dest_city, economy.return_number, economy.return_date, economy.total_days,
                                                  economy.seat, economy.price, short_url)
                        print("Dynamo Table Updated")

                        # Email Message
                        send_alert(economy, short_url, dest_code)
                        print('Text/Email sent\n')

                    else:
                        print(f'No flight found to {dest_city}\n')
                        fdb.close()

                except Exception:
                    print()
                    continue


if __name__ == '__main__':
    Back()
