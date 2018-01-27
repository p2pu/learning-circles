from django.conf.urls import include, url
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from .forms import CustomPasswordResetForm
from .views import SignupApiView


urlpatterns = [
    url(r'^register/', SignupApiView.as_view(), name='signup_api'),
    url(r'^login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url(r'^password_reset/$', PasswordResetView.as_view(form_class=CustomPasswordResetForm), name="password_reset"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(post_reset_login=True, success_url=reverse_lazy('studygroups_login_redirect') ), name='password_reset_confirm'),
    url(r'^', include('django.contrib.auth.urls')),
]
