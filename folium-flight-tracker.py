import requests
import pandas as pd
import csv
from math import radians, cos, sin, asin, sqrt
from flask import Flask
import folium
import folium.plugins as plugins

app = Flask(__name__)

#START OF CUSTOMIZATION SECTION
url = "YOUR AIRLABS.CO API KEY"

#this is for the deafult coloring of the planes
default_color = 'gray'

#just an example for the airports in the DCA area. Make sure to add a duplicate set for icaos with a "K" at the beginning!
airport_colors = {
    'DCA': 'green',
    'IAD': 'blue',
    'BWI': 'purple',
    'KDCA': 'green',
    'KIAD': 'blue',
    'KBWI': 'purple',
    'other': 'gray',
}

center_lat = YOUR_LAT
center_lon = YOUR_LON
#END OF CUSTOMIZATION SECTION

response = requests.get(url)
response_dict = response.json()["response"]

header_written = False
num_of_flights = int(input("Number of flights: "))
distance_from_home = int(input("Search radius: "))
flights = 0

earth_radius_miles = 3963
earth_radius_km = 6371


# from geeksforgeeks.org/program-distance-two-points-earth/
def distance_between_two_latlon(lat1, lon1, lat2, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # use earth_radius_km for kilometers
    r = earth_radius_miles

    # calculate the result
    return c * r


# creates "flight_data" csv file
with open("flight_data.csv", "w") as f:
    # loops through the data in the data dictionary
    for data in response_dict:
        # check if the airplane is in the air. If so, check if the distance is between the plane and you is close enough
        if (
            distance_between_two_latlon(
                center_lat, center_lon, data["lat"], data["lng"]
            )
            < distance_from_home
        ):
            # checks if the amount of flights you inputed is less than the flights looped
            if flights <= num_of_flights:
                # initiate the csv writer
                w = csv.DictWriter(f, data.keys())
                # write a header if it hasnt been written yet.
                if not header_written:
                    w.writeheader()

                # write data
                w.writerow(data)

                # make sure we don't repeat headers and loop through too many flights.
                header_written = True
                flights += 1


# read flight data csv
flight_data = pd.read_csv("flight_data.csv")

# you can add whatever you want to keys that will be looked at in the csv file. hex, reg_number, flag, lat, lng, alt, dir, speed, v_speed, squawk,
# flight_number, flight_icao, flight_iata, dep_icao, dep_iata, arr_icao, arr_iata, airline_icao, airline_iata,
# aircraft_icao, updated, status (to list them all)
keys = (
    "lat",
    "lng",
    "flight_icao",
    "dir",
    "alt",
    "arr_iata",
    "aircraft_icao",
    "dep_iata",
    "speed",
)
flight_records = []

# read the csv file and add all the data we want into a dictionary.
with open("flight_data.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        flight_records.append({key: row[key] for key in keys})


@app.route("/")
def map_marker():
    map = folium.Map(
        location=[center_lat, center_lon],
        # there are other tiles you can use such as openstreetmap.
        tiles="Stamen Terrain",
        zoom_start=20,
    )

    for flight in flight_records:
        coords = (flight['lat'], flight['lng'])

        #Gets the departure airport and the arrival airport. (Private jetts and other airplanes with no flight number won't some data shared to the public. That causes the dep_iata or arr_iata to sometimes be en-route or something)
        dep_iata = flight['dep_iata'] if flight['dep_iata'] is not None else 'other'
        arr_iata = flight['arr_iata'] if flight['arr_iata'] is not None else 'other'

        #default color. you can change this by going to the "default_color variable up top"
        color = default_color

        #check to see if the color is in the airport_colors dictionary
        if dep_iata in airport_colors.keys():
            #changes the color to the respected color of the airprot
            dep_color = airport_colors.get(dep_iata)
        else:
            #make the color the default
            dep_color = default_color

        #same thing here except for arrival iatas
        if arr_iata in airport_colors.keys():
            arr_color = airport_colors.get(arr_iata)
        else:
            arr_color = default_color

        #changes the planes color
        if dep_color != default_color:
            color = dep_color
        elif arr_color != default_color:
            color = arr_color
            
        # define our plane icon and the custom settings
        plane_icon = plugins.BeautifyIcon(
            icon="plane",
            border_color="transparent",
            background_color="transparent",
            border_width=1,
            text_color=color,
            inner_icon_style="margin:0px;font-size:2em;transform: rotate({0}deg);".format(
                float(flight["dir"]) - 90 if float(flight["dir"]) - 90 is not None else 'No data'
            ),
        )
        # to add more data when you click a flight, add another %s. Then in the parentheses add the data you want to inset. EXAMPLE: "Altitude: %s \n Direction: %s \n From: %s" % (flight['alt'], flight['dir'], flight['dep_iata'])
        folium.Marker(
            coords,
            tooltip=flight["flight_icao"],
            icon=plane_icon,
            popup="Altitude: %s \n Direction: %s \n Speed (knots): %s" 
            % (
                flight["alt"], 
                flight["dir"],
                round(float(flight["speed"]) * 0.539957, 2),
            )
        ).add_to(map)

    return map._repr_html_()

# run the app
app.run(debug=True)
