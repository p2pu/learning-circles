from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(r'^s3direct/', include('s3direct.urls')),
)

urlpatterns += i18n_patterns('',
    url(r'^', include('studygroups.urls')),
    url(r'^interest/', include('interest.urls', namespace='interest')),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name="about"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^ux/', include('uxhelpers.urls'))
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {
             'document_root': settings.MEDIA_ROOT,
         }),
    )

