from django.core.management.base import BaseCommand, CommandError

from cities.google import google_places_api
from cities import data
from studygroups.models import StudyGroup
import requests

keys = ["place_id", "city", "region", "country", "country_en", "latitude", "longitude"]

data_fixes = {
    "Chicago, Illinois, United States": dict(zip(keys, ["4887398", "Chicago", "Illinois", "United States of America", "United States of America", 41.875500, -87.624500])),
    "Chicago, Illinois, United States of America": dict(zip(keys, ["4887398", "Chicago", "Illinois", "United States of America", "United States of America", 41.875500, -87.624500])),
    "Chicago": dict(zip(keys, ["4887398", "Chicago", "Illinois", "United States of America", "United States of America", 41.875500, -87.624500])),
    "Nakuru, Kenya": dict(zip(keys, ["184622", "Nakuru", "Nakuru", "Kenya", "Kenya", -0.307190, 36.072250])),
    "Boston, Massachusetts, United States of America":  dict(zip(keys, ["4930956", "Boston", "Massachusetts", "United States of America", "United States of America", 42.358430, -71.059770])),
    "Toronto, Ontario, Canada": dict(zip(keys, ["6167865", "Toronto", "Ontario", "Canada", "Canada", 43.653900, -79.387300])),
    "Detroit, Michigan, United States of America": dict(zip(keys, ["4990729", "Detroit", "Michigan", "United States of America", "United States of America", 42.331430, -83.045750])),
    "Detroit, Michigan, United States": dict(zip(keys, ["4990729", "Detroit", "Michigan", "United States of America", "United States of America", 42.331430, -83.045750])),
    "Detroit, MI": dict(zip(keys, ["4990729", "Detroit", "Michigan", "United States of America", "United States of America", 42.331430, -83.045750])),
    "Wichita, Kansas, United States of America": dict(zip(keys, ["4281730", "Wichita", "Kansas", "United States of America", "United States of America", 37.692200, -97.337600])),
    "Kansas City, Missouri, United States of America": dict(zip(keys, ["4273837", "Kansas City", "Missouri", "United States of America", "United States of America", 39.100100, -94.578200])),
    "Kansas City": dict(zip(keys, ["4273837", "Kansas City", "Missouri", "United States of America", "United States of America", 39.100100, -94.578200])),
    "Nairobi, Nairobi Area, Kenya": dict(zip(keys, ["184745", "Nairobi", "Nairobi", "Kenya", "Kenya", -1.283300, 36.817200])),
    "Nairobi, Kenya": dict(zip(keys, ["184745", "Nairobi", "Nairobi", "Kenya", "Kenya", -1.283300, 36.817200])),
    "Charlotte, North Carolina, United States of America": dict(zip(keys, ["4460243", "Charlotte", "North Carolina", "United States of America", "United States of America", 35.227000, -80.843200])),
    "San Jose, California, United States of America": dict(zip(keys, ["5392171", "San Jose", "California", "United States of America", "United States of America", 37.339390, -121.894960])),
    "Providence, Rhode Island, United States of America": dict(zip(keys, ["5224151", "Providence", "Rhode Island", "United States of America", "United States of America", 41.823990, -71.412830])),
    "Cleveland, Ohio, United States of America": dict(zip(keys, ["5150529", "Cleveland", "Ohio", "United States of America", "United States of America", 41.505100, -81.693500])),
    "Narok, Kenya": dict(zip(keys, ["184379", "Narok", "Narok", "Kenya", "Kenya", -1.087200, 35.872600])),
    "Virginia Beach, Virginia, United States of America": dict(zip(keys, ["4791259", "Virginia Beach", "Virginia", "United States of America", "United States of America", 36.852900, -75.977500])),
    "Nanyuki, Laikipia, Kenya": dict(zip(keys, ["184433", "Nanyuki", "Laikipia", "Kenya", "Kenya", 0.006240, 37.073980])),
    "Kericho, Kenya": dict(zip(keys, ["192900", "Kericho", "Kericho", "Kenya", "Kenya", -0.366600, 35.283300])),
    "Lakewood, Washington, United States of America": dict(zip(keys, ["5800420", "Lakewood", "Washington", "United States of America", "United States of America", 47.171800, -122.518000])),
    "Philadelphia, Pennsylvania, United States of America": dict(zip(keys, ["4560349", "Philadelphia", "Pennsylvania", "United States of America", "United States of America", 39.952700, -75.163500])),
    "Paris, Île-de-France, France": dict(zip(keys, ["af9599b85ad97dcead64bbb7bc500445", "Paris", "Île-de-France", "France", "France", 48.854600, 2.347710])),
}


class Command(BaseCommand):
    help = 'Fix old location data that was not geolocated'

    def handle(self, *args, **options):
        for key, value in data_fixes.items():
            study_groups = StudyGroup.objects.filter(city=key, place_id='')
            print(f'{key}, {study_groups.count()}')
            print(value)
            print()
            study_groups.update(**value)
