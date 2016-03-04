import cities as c

from utils import json_response

# jQuery autocomplete for city names
def city_complete(request):
    # response format 'City name, region code, country name'
    callback = request.GET.get('callback')
    q = request.GET.get('q')
    matches = [ city for city in c.read_autocomplete_list() if city.find(q) != -1 ]
    return json_response(request, matches)
