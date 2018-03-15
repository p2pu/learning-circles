import codecs

def read_admin1_codes():
    import unicodecsv
    with open('cities/admin1CodesASCII.txt', 'rb') as csvfile:
        reader = unicodecsv.reader(csvfile, delimiter='\t', encoding='utf-8')
        data = list(reader)
    return data


def read_cities():
    import unicodecsv
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


def read_autocomplete_list():
    with codecs.open('cities/autocomplete_list.csv', 'r', 'utf-8') as f:
        autocomplete_list = [l.strip('\n') for l in f]
    return autocomplete_list


def update_autocomplete_list():
    import geonamescache
    admin1 = read_admin1_codes()
    def admin1_name(code):
        return next((a[1] for a in admin1 if a[0] == code), None) or ''

    gc = geonamescache.GeonamesCache()
    cities = [
        ', '.join([
            city['name'],
            admin1_name(city['country code'] + '.' + city['admin1 code']),
            gc.get_countries()[city['country code']]['name']
        ])
        for city in read_cities()
    ]
    with codecs.open('cities/autocomplete_list.csv', 'w', 'utf-8') as f:
        f.write('\n'.join(cities))

