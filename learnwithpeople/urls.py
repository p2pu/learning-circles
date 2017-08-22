from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.i18n import javascript_catalog
from django.contrib.auth import views as auth_views
from studygroups.registration import CustomPasswordResetForm

js_info_dict = {
    'packages': ('studygroups',),
}

urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name="about"),
    url(r'^accounts/login/', auth_views.login, name='login', kwargs={'redirect_authenticated_user': True}),
    url(r'^accounts/password_reset/$', auth_views.password_reset,
        {'password_reset_form': CustomPasswordResetForm},
        name="password_reset"
    ),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),
    url(r'^', include('studygroups.urls'))
)

urlpatterns += [
    url(r'^api/', include('api.urls')),
]

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    from django.views.static import serve
    urlpatterns += [
        url(r'^%s/(?P<path>.*)$' % media_url, serve,
           {
               'document_root': settings.MEDIA_ROOT,
           }
        ),
    ]

