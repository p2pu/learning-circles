from django.urls import re_path, include

from rest_framework import routers
from .api import EventViewSet

router = routers.DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    re_path(r'^', include(router.urls)),
    #re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
