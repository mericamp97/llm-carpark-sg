import pandas as pd
import requests

from location import get_current_location

auth_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI4NGMzZmJmYjdiYjhiN2JiNmY0NWQ3NTUwZDgxOTk1YSIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC0xMjIzNjk4OTkyLmFwLXNvdXRoZWFzdC0xLmVsYi5hbWF6b25hd3MuY29tL2FwaS92Mi91c2VyL3Bhc3N3b3JkIiwiaWF0IjoxNzEwOTE4NTM2LCJleHAiOjE3MTExNzc3MzYsIm5iZiI6MTcxMDkxODUzNiwianRpIjoiRGRDeUhFTFR1REl6eTFmbyIsInVzZXJfaWQiOjI5OTQsImZvcmV2ZXIiOmZhbHNlfQ.jD4rKbaFbp0rgtUz8ei-7z3qb41gSDuEPLaQVIywk20"
import pandas as pd
from haversine import haversine, Unit

def get_route(start_lat, start_lon, end_lat, end_lon, token):
    url = f"https://www.onemap.gov.sg/api/public/routingsvc/route?start={start_lat}%2C{start_lon}&end={end_lat}%2C{end_lon}&routeType=drive"
    headers = {"Authorization": token}
    response = requests.request("GET", url, headers=headers)
    return response.text
def get_route_for_row(row,end_lat,end_lon):
    start_lat = row['Latitude']
    start_lon = row['Longitude']
    return get_route(start_lat, start_lon, end_lat, end_lon, auth_token)
def calculate_distance(row,current_lat,current_lon):
    coords_1 = (row['Latitude'], row['Longitude'])
    coords_2 = (current_lat, current_lon)
    return haversine(coords_1, coords_2, unit=Unit.MILES)

def get_top_dataframe(current_lat,current_lon,df):
    df['distance_to_carpark'] = df.apply(calculate_distance,args=(current_lat, current_lon), axis=1)
    shortest_rows = df.nsmallest(10, 'distance_to_carpark')
    end_lat=current_lat
    end_lon=current_lon
    shortest_rows['route_directions'] = shortest_rows.apply(get_route_for_row,args=(current_lat, current_lon),axis=1)
    return shortest_rows

# g= get_current_location()
# df1 = pd.read_csv("./data/carParkLocation.csv")
# df = get_top_dataframe(g['current_location'][0],g['current_location'][1],df1)


