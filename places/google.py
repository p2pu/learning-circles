import requests
from django.conf import settings


def google_places_api(city):
    params = {
        "query": city,
        "key": settings.GOOGLE_API_KEY
    }
    r = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
    return r.json()


def example_data():
    data = {
        "html_attributions" : [],
        "results" : [
            {
                "formatted_address" : "Chicago, IL, USA",
                "geometry" : {
                    "location" : {
                        "lat" : 41.8781136,
                        "lng" : -87.6297982
                        },
                    "viewport" : {
                        "northeast" : {
                            "lat" : 42.023131,
                            "lng" : -87.52366099999999
                            },
                        "southwest" : {
                            "lat" : 41.6443349,
                            "lng" : -87.9402669
                            }
                        }
                    },
                "icon" : "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
                "id" : "53eeb015d61056c54245a909c79862532fc953ad",
                "name" : "Chicago",
                "photos" : [
                    {
                        "height" : 2204,
                        "html_attributions" : [
                            "\\u003ca href=\"https://maps.google.com/maps/contrib/116900064763385163773/photos\"\\u003eLonglong Tian\\u003c/a\\u003e"
                            ],
                        "photo_reference" : "CmRaAAAAwFcb4Zx8z1OIdCg2KCgSWp-aTACZ4fY5BBH8pVWXhVI1mH7uTuP8_VKoo2SIBOD7CqVYpCVIpOq8kIZDE-PwdFkx1u4K6tmjOxjg0qrwOB3p9W-gap28vAMAeorO6O-hEhAq5qRzIswsE7tBMyTaB8UJGhRnA5j3DIn84sY3judh5s4FqooJzQ",
                        "width" : 3920
                        }
                    ],
                "place_id" : "ChIJ7cv00DwsDogRAMDACa2m4K8",
                "reference" : "CmRbAAAAc2HHY6bqnWbs1oWY9ub5DD6iONmo0GpQH8wlRRzBKR_V0q1fuIysLidjPY7_CBgqcWjgDeUpfgRQNktmhiRKWl4UYOPHL6cCOB2TF-ex7Jy1vD4rSd6wsT7MWPP4e1CtEhCd2mdgo9r-xQDXkKXvDVD5GhQY6Hqx4RF8HowEMANtz68tdupGRQ",
                "types" : [ "locality", "political" ]
                }
            ],
        "status" : "OK"
    }
