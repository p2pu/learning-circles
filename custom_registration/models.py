from django.contrib.auth.models import User
import random
import string

from studygroups.models import Facilitator

def create_user(email, first_name, last_name, mailing_list_signup):
    user = User.objects.create_user(
        email.lower(), #use lowercase email as username
        email, #keep email in original case supplied
        "".join([random.choice(string.letters) for i in range(64)])
    )
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    facilitator = Facilitator(user=user) 
    facilitator.mailing_list_signup = mailing_list_signup
    facilitator.save()
    return user
