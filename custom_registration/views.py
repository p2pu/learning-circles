from django import http
from django.views import View
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect

import json

from uxhelpers.utils import json_response
from api import schema
from .models import create_user
from .models import check_user_token
from .models import confirm_user_email
from .models import send_email_confirm_email
from .forms import SignupForm
from .decorators import user_is_not_logged_in

# TODO make sure user is not signed in!!
@method_decorator(user_is_not_logged_in, name='dispatch')
class SignupView(FormView):
    form_class = SignupForm
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'custom_registration/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user = create_user(user.email, user.first_name, user.last_name, form.cleaned_data['password1'], form.cleaned_data['newsletter'])
        login(self.request, user)
        return http.HttpResponseRedirect(self.get_success_url())


@method_decorator(csrf_exempt, name='dispatch')
class SignupApiView(View):

    def post(self, request):
        def _user_check():
            def _validate(value):
                error = _('A user with that email address already exists.')
                if User.objects.filter(username__iexact=value).exists():
                    return None, error
                return value, None
            return _validate
        post_schema = {
            "email": schema.chain([
                schema.email(required=True),
                _user_check(),
            ]),
            "first_name": schema.text(required=True),
            "last_name": schema.text(required=True),
            "password": schema.text(required=True),
            "newsletter": schema.boolean(required=True),
        }
        data = json.loads(request.body)
        data, errors = schema.validate(post_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        user = create_user(data['email'], data['first_name'], data['last_name'], data['password'], data['newsletter'])
        login(request, user)
        return json_response(request, { "status": "created", "user": user.username });


@method_decorator(login_required, name='dispatch')
class EmailConfirmRequestView(View):

    def post(self, request, *args, **kwargs):
        send_email_confirm_email(request.user)
        messages.success(self.request, _('Verification email sent. Please check your inbox and follow instructions.'))
        url = reverse('studygroups_facilitator')
        return HttpResponseRedirect(url)


class EmailConfirmView(View):
    """ View mostly copied from Django password reset confirm view """

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def get(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs
        user = self.get_user(kwargs['uidb64'])
        if user is not None:
            token = kwargs['token']
            if self.request.user.is_authenticated() and user.pk != self.request.user.pk:
                # make sure logged in user and user confirming emails are the same people
                messages.warning(self.request, _('There is a problem with your password confirmation ULR. Please try logging out and then click the link in the email we sent you.'))
                url = reverse('studygroups_login_redirect')
                return HttpResponseRedirect(url)

                
            if check_user_token(user, token):
                # Set email address to confirmed in profile
                if user.facilitator.email_confirmed_at != None:
                    # redirect user to login page
                    # NB! Don't log user in, since link could have leaked and hash isn't gauranteed to change after the user confirms their email address
                    messages.success(self.request, _('Your email address has been already been confirmed.'))
                    url = reverse('studygroups_login_redirect')
                    return HttpResponseRedirect(url)
                else:
                    confirm_user_email(user)
                    login(self.request, user)
                    messages.success(self.request, _('Your email address has been confirmed!.'))
                    # redirect them to dashboard
                    url = reverse('studygroups_facilitator')
                    return HttpResponseRedirect(url)

        messages.warning(self.request, _('Invalid email confirmation URL.'))
        url = reverse('login')
        return HttpResponseRedirect(url)


    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user
