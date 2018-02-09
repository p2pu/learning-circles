from django.conf.urls import include, url
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from .forms import CustomPasswordResetForm
from .views import SignupView
from .views import AjaxSignupView
from .views import AjaxLoginView
from .views import EmailConfirmRequestView
from .views import EmailConfirmView


urlpatterns = [
    url(r'^fe/register/', AjaxSignupView.as_view(), name='fe_register'),
    url(r'^fe/login/', AjaxLoginView.as_view(), name='fe_login'),
    url(r'^register/', SignupView.as_view(), name='register'),
    url(r'^email_confirm/$', EmailConfirmRequestView.as_view(), name="email_confirm_request"),
    url(r'^email_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', EmailConfirmView.as_view(), name="email_confirm"),
    url(r'^login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url(r'^password_reset/$', PasswordResetView.as_view(form_class=CustomPasswordResetForm), name="password_reset"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(post_reset_login=True, success_url=reverse_lazy('studygroups_login_redirect') ), name='password_reset_confirm'),
    url(r'^', include('django.contrib.auth.urls')),
]
