import geocoder
import json

def get_current_location():
    # Get GPS coordinates using the geocoder library
    location = geocoder.ip('me')

    if not location:
        print("Error: Unable to determine current location.")
        return

    #latitude, longitude = location.latlng
    dict = {'current_location': location.latlng}
    return dict

print(type(get_current_location()['current_location'][0]))
