import requests
import pandas as pd
import plotly.express as px
import csv
from math import radians, cos, sin, asin, sqrt

#change this
url = "AIR LABS KEY (airlabs.co)"

response = requests.get(url)
response_dict = response.json()['response']

header_written = False
num_of_flights = int(input('Number of flights: '))
distance_from_home = int(input('Search radius: '))
flights = 0

#change this
center_lat = YOUR_LAT
center_lon = YOUR_LON

earth_radius_miles = 3963
earth_radius_km = 6371

#from geeksforgeeks.org/program-distance-two-points-earth/
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
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))

    #use earth_radius_km for kilometers
    r = earth_radius_miles
      
    # calculate the result
    return(c * r)

#creates "flight_data" csv file
with open('flight_data.csv', 'w') as f:
    #loops through the data in the data dictionary
    for data in response_dict:
        #check if the airplane is in the air. If so, check if the distance is between the plane and you is close enough
        if 'status' in data.keys() and data['status'] == 'en-route' and distance_between_two_latlon(center_lat, center_lon, data['lat'], data['lng']) < distance_from_home:
            #checks if the amount of flights you inputed is less than the flights looped
            if flights <= num_of_flights:
                #initiate the csv writer
                w = csv.DictWriter(f, data.keys())
                #write a header if it hasnt been written yet.
                if not header_written:
                    w.writeheader()

                #write data
                w.writerow(data)

                #make sure we don't repeat headers and loop through too many flights.
                header_written = True
                flights += 1


#read flight data csv
flight_data = pd.read_csv("flight_data.csv")

#initiate our plotly scatter mapbox
fig = px.scatter_mapbox(
    flight_data, 
    lat="lat", 
    lon="lng", 
    #you can change this to whatever you want. hex, reg_number, flag, lat, lng, alt, dir, speed, v_speed, squawk, 
    #flight_number, flight_icao, flight_iata, dep_icao, dep_iata, arr_icao, arr_iata, airline_icao, airline_iata, 
    #aircraft_icao, updated, status (to list them all)
    hover_name="flight_icao", 
    color_discrete_sequence=["fuchsia"], 
    size_max=100,
    zoom=5, 
    height=1000
)

#open the map and show it
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
