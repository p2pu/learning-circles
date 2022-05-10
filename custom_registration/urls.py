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
from .views import WhoAmIView
from .views import AccountSettingsView
from .views import AccountDeleteView


urlpatterns = [
    url(r'^fe/register/', AjaxSignupView.as_view(), name='fe_register'),
    url(r'^fe/login/', AjaxLoginView.as_view(), name='fe_login'),
    url(r'^fe/whoami/', WhoAmIView.as_view(), name='fe_whoami'),
    url(r'^register/', SignupView.as_view(), name='register'),
    url(r'^email_confirm/$', EmailConfirmRequestView.as_view(), name="email_confirm_request"),
    url(r'^email_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$', EmailConfirmView.as_view(), name="email_confirm"),
    url(r'^login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url(r'^password_reset/$', PasswordResetView.as_view(form_class=CustomPasswordResetForm), name="password_reset"),
    url(r'^settings/$', AccountSettingsView.as_view(), name="account_settings"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$', PasswordResetConfirmView.as_view(post_reset_login=True, success_url=reverse_lazy('studygroups_login_redirect') ), name='password_reset_confirm'),
    url(r'^delete/$', AccountDeleteView.as_view(), name='account_delete'),
    url(r'^', include('django.contrib.auth.urls')),
]
