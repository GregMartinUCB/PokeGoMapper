from google.protobuf.internal import encoder
from s2sphere import *
from geopy.geocoders import GoogleV3
import struct


class LocationSetter:

    COORDS_LATITUDE = 0
    COORDS_LONGITUDE = 0
    COORDS_ALTITUDE = 0
    FLOAT_LAT = 0 
    FLOAT_LONG = 0

    @staticmethod
    def f2i(float):
        return struct.unpack('<Q', struct.pack('<d', float))[0]

    @staticmethod
    def f2h(float):
        return hex(struct.unpack('<Q', struct.pack('<d', float))[0])

    @staticmethod
    def h2f(hex):
        return struct.unpack('<d', struct.pack('<Q', int(hex,16)))[0]

    @staticmethod
    def set_location(location_name):
        geolocator = GoogleV3()
        loc = geolocator.geocode(location_name, timeout = 10)

        

        print('[!] Your given location: {}'.format(loc.address.encode('utf-8')))
        print('[!] lat/long/alt: {} {} {}'.format(loc.latitude, loc.longitude, loc.altitude))
        LocationSetter.set_location_coords(loc.latitude, loc.longitude, loc.altitude)

    @staticmethod
    def set_location_coords(lat, long, alt):
        
        LocationSetter.FLOAT_LAT = lat
        LocationSetter.FLOAT_LONG = long
        LocationSetter.COORDS_LATITUDE = LocationSetter.f2i(lat) # 0x4042bd7c00000000 # f2i(lat)
        LocationSetter.COORDS_LONGITUDE = LocationSetter.f2i(long) # 0xc05e8aae40000000 #f2i(long)
        LocationSetter.COORDS_ALTITUDE = LocationSetter.f2i(alt)

    @staticmethod
    def get_location_coords():
        return (LocationSetter.COORDS_LATITUDE, LocationSetter.COORDS_LONGITUDE, LocationSetter.COORDS_ALTITUDE)