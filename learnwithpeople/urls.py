from django.urls import re_path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from django.urls import reverse, reverse_lazy

urlpatterns = i18n_patterns(
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/', include('custom_registration.urls')),
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=['studygroups']), name='javascript-catalog'),
    re_path(r'^discourse/', include('discourse_sso.urls')),
    re_path(r'^surveys/', include('surveys.urls')),
    re_path(r'^community_calendar/', include('community_calendar.urls')),
    re_path(r'^courses/', include('courses.urls')),
    re_path(r'^', include('studygroups.urls'))
)

urlpatterns += [
    re_path(r'^api/', include('studygroups.api_urls')),
    re_path(r'^api/', include('contact.urls')),
    re_path(r'^api/places/', include('places.urls')),
    re_path(r'^api/community_calendar/', include('community_calendar.api_urls')),
    re_path(r'^announce/', include('announce.urls')),
    re_path(r'^log/', include('client_logging.urls')),
    re_path(r'^tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    static_url = settings.STATIC_URL.lstrip('/').rstrip('/')
    from django.views.static import serve
    urlpatterns += [
        re_path(r'^%s/(?P<path>.*)$' % media_url, serve,
           {
               'document_root': settings.MEDIA_ROOT,
           }
        ),
        re_path(r'^%s/(?P<path>.*)$' % static_url, serve,
           {
               'document_root': settings.STATIC_ROOT,
           }
        ),
    ]

