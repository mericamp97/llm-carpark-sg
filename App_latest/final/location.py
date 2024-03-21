import geocoder
import json

# Get user's current location
def get_current_location():
    # Get GPS coordinates using the geocoder library
    location = geocoder.ip('me')

    if not location:
        print("Error: Unable to determine current location.")
        return

    #latitude, longitude = location.latlng
    dict = {'current_location': location.latlng}
    return dict

# call location and write it in data folder for indexing in case required.
def get_loc():
    loc = get_current_location()
    print(loc)
    with open('../data/current_location.json', 'w') as file:
        json.dump(loc, file)

