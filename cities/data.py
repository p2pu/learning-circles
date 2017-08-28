import codecs
import unicodecsv
import geonamescache

def read_admin1_codes():
    with open('cities/admin1CodesASCII.txt', 'rb') as csvfile:
        reader = unicodecsv.reader(csvfile, delimiter='\t', encoding='utf-8')
        data = list(reader)
    return data


def read_cities():
    # See http://download.geonames.org/export/dump/readme.txt
    geoname_header = [
        'geonameid',
        'name',
        'asciiname',
        'alternatenames',
        'latitude',
        'longitude',
        'feature class',
        'feature code',
        'country code',
        'cc2',
        'admin1 code',
        'admin2 code',
        'admin3 code',
        'admin4 code',
        'population',
        'elevation',
        'dem',
        'timezone',
        'modification date',
    ]
    with open('cities/cities15000.txt', 'rb') as csvfile:
        reader = unicodecsv.DictReader(csvfile, geoname_header, delimiter='\t', encoding='utf-8')
        data = list(reader)
    return data


def update_city_list():
    admin1 = read_admin1_codes()
    def admin1_name(code):
        return next((a[1] for a in admin1 if a[0] == code), None) or ''

    gc = geonamescache.GeonamesCache()
    cities = [
        [
            city['name'],
            admin1_name(city['country code'] + '.' + city['admin1 code']),
            gc.get_countries()[city['country code']]['name'],
            city['latitude'],
            city['longitude'],
        ]
        for city in read_cities()
    ]
    with open('cities/city_list.csv', 'w') as f:
        writer = unicodecsv.writer(f, encoding='utf-8')
        writer.writerows(cities)


def read_city_list():
    with open('cities/city_list.csv', 'r') as csvfile:
        reader = unicodecsv.reader(csvfile, encoding='utf-8')
        data = list(reader)
    return data

    with codecs.open('cities/city_list.csv', 'r', 'utf-8') as f:
        autocomplete_list = [l.strip('\n') for l in f]
    return autocomplete_list


def find_city(city, region, country):
    city_list = read_city_list()
    if country == 'United States of America':
        country = 'United States'

    # Look for exact match
    exa = [data for data in city_list if city == data[0] and region == data[1] and country == data[2]]
    if len(exa) == 1:
        return exa

    res1 = [data for data in city_list if city in data]
    res2 = [data for data in res1 if country in data]
    if len(res2) == 0:
        return res1
    res3 = [data for data in res2 if region in data]
    if len(res3) == 0:
        return res2
    return res3
