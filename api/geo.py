from math import radians, cos, sin, asin, sqrt
import math


def getLatLonDelta(lat, lon, distance):
    """ 
    calculate detla lat, lon for finding other lat, lons in given distance-ish
    """
    earth_radius = 6366.0
    km_per_lat = 2*math.pi*earth_radius/360.0 #approx 111 km per degree longitude
    lat_delta = min(distance/km_per_lat, 180)
    # Use circumference at latitue to calculate distance per degree longitude
    c = 2*math.pi*earth_radius/360.
    km_per_lon_mid = c*cos(radians(lat))
    # avoid divide by zero
    lon_delta = min(distance/max(0.001,km_per_lon_mid), 360)
    # print('At latitude {}, latitude lines are {} km long, thus every degree longitude corresponds to {} km'.format(lat, 360*km_per_lon_mid, km_per_lon_mid))
    return (lat_delta, lon_delta)
    # NOTE: km/longitude will differ at lat+lat_delta and lat-lat_delta
    # for now we're ignoring that
    # km_per_lon_top = c*cos(radians(lat+lat_delta))
    # lon_delta_top = distance/km_per_lon_top
    # km_per_lon_bot = c*cos(radians(lat-lat_delta))
    # lon_delta_bot = distance/km_per_lon_bot
    # lon_delta = max(lon_delta_top, lon_delta_bot)
    # return (lat_delta, lon_delta)
