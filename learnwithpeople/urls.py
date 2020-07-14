from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from django.urls import reverse, reverse_lazy

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('custom_registration.urls')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=['studygroups']), name='javascript-catalog'),
    url(r'^discourse/', include('discourse_sso.urls')),
    url(r'^surveys/', include('surveys.urls')),
    url(r'^community_calendar/', include('community_calendar.urls')),
    url(r'^', include('studygroups.urls'))
)

urlpatterns += [
    url(r'^api/', include('studygroups.api_urls')),
    url(r'^api/community_calendar/', include('community_calendar.api_urls')),
    url(r'^announce/', include('announce.urls')),
    url(r'^log/', include('client_logging.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    static_url = settings.STATIC_URL.lstrip('/').rstrip('/')
    from django.views.static import serve
    urlpatterns += [
        url(r'^%s/(?P<path>.*)$' % media_url, serve,
           {
               'document_root': settings.MEDIA_ROOT,
           }
        ),
        url(r'^%s/(?P<path>.*)$' % static_url, serve,
           {
               'document_root': settings.STATIC_ROOT,
           }
        ),
    ]

