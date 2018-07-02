from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.views.i18n import javascript_catalog
from django.urls import reverse, reverse_lazy

js_info_dict = {
    'packages': ('studygroups',),
}

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('custom_registration.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),
    url(r'^discourse/', include('discourse_sso.urls')),
    url(r'^', include('studygroups.urls'))
)

urlpatterns += [
    url(r'^api/', include('api.urls')),
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

