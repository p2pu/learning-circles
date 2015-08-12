from django.shortcuts import render
from django import http

from interest.models import Lead
import json

# Create your views here.
def sync(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        lead = None
        if 'id' in request.POST:
            lead_data = { key:json.dumps(value) for key,value in request.POST.iterlists() if key in ['course', 'location', 'time'] }
            leads = Lead.objects.filter(id=request.POST.get('id'))
            leads.update(**lead_data)
            lead = leads[0]
        elif 'email' in post_data or 'mobile' in post_data or 'contact' in post_data:
            # TODO return error if data is missing - need at least name AND email or mobile
            # TODO check if email is already signed up, if so, update previous signup
            # Create a new lead
            lead_data = {key:value for key,value in post_data.items() if key in ['email', 'mobile', 'name', 'utm']}
            lead = Lead.objects.create(**lead_data)
        else:
            return http.HttpResponse(status=400)
            
        # See if the lead included an ID, if it does, update the id
        # for every field in the post, update the model
        # return ID and step?
        return http.JsonResponse({"id": lead.id})
    return http.HttpResponse(status=403)
