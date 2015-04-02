from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(r'^s3direct/', include('s3direct.urls')),
)


urlpatterns += i18n_patterns('',
    url(r'^', include('studygroups.urls')),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name="about"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)
