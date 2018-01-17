import phonenumbers
import re
from datetime import datetime
from decimal import Decimal

def _required(func):
    def decorator(*args, **kwargs):
        required = kwargs.get('required', False)
        if 'required' in kwargs:
            del kwargs['required']
        def required_validator(data):
            if required and data is None:
                return None, 'Field is required'
            if not required and data is None:
                return None, None
            # actual validator is now only created during validation
            return func(*args, **kwargs)(data)
        return required_validator
    return decorator


@_required
def integer():
    def _validate(value):
        error = 'Not a valid integer'
        if value is None:
            return None, error
        try:
            n = int(value)
            return n, None
        except ValueError:
            return None, error
    return _validate


@_required
def floating_point():
    def _validate(value):
        error = 'Not a valid float'
        if value is None:
            return None, error
        try:
            f = float(value)
            return f, None
        except ValueError:
            return None, error
    return _validate


@_required
def text(length=None):
    def _validate(string):
        if length and len(string) > length:
            return None, 'String too long'
        return string, None
    return _validate


@_required
def date(format='%Y-%m-%d'):
    error = 'Not a valid date'
    def _validate(data):
        try:
            date = datetime.strptime(data, format).date()
            return date, None
        except ValueError:
            return None, error
    return _validate


@_required
def time(format='%H:%M'):
    error = 'Not a valid time'
    def _validate(data):
        try:
            time = datetime.strptime(data, format).time()
            return time, None
        except ValueError:
            return None, error
    return _validate


@_required
def email():
    def _validate(email):
        error = 'Invalid email address'
        if email == None:
            return None, None # Not sure if this is correct?
        if email.count('@') != 1:
            return None, error
        user, domain = email.split('@')
        # Regular expressions lifted from Django django.core.validators
        user_re = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
            re.IGNORECASE)
        domain_re = re.compile(r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z', re.IGNORECASE)
        if user_re.match(user) is None or domain_re.match(domain) is None:
            return None, error
        return email, None

    return _validate


@_required
def mobile():
    def _validate(mobile):
        if mobile is None:
            return None
        try:
            nr = phonenumbers.parse(mobile, None)
            if phonenumbers.is_valid_number(nr) is False:
                return 'Not a valid phone number'
            return rn, None
        except phonenumbers.phonenumberutil.NumberParseException:
            return None, 'Not a valid phone number'
    return _validate


@_required
def chain(checks):
    """ Chain multiple checks. Result from last check is returned as data """
    def _validate(data):
        errors = []
        parsed = None
        for check in checks:
            parsed, error = check(data)
            if error != None:
                errors += [error]
        if errors != []:
            return None, errors
        return parsed, None
    return _validate


#TODO choice validator


@_required
def schema(schema):
    def _validate(data):
        return validate(schema, data if data else {})
    return _validate


def validate(schema, data):
    """ Validate a schema
    schema = {
        'field name 1': validator function,
        'field name 2': [
            validation function 1,
            validation function 2,
        ],
        'example email field', email
    }
    """
    cleaned_data = {}
    errors = {}
    for field, validator in schema.iteritems():
        parsed, error = validator(data.get(field))
        if error != None and error != [] and error != {}:
            if type(error) == type([]):
                errors[field] = error
            else:
                errors[field] = [error]
        else:
            cleaned_data[field] = parsed

    # TODO - errors for extra fields
    return cleaned_data, errors


def django_get_to_dict(get):
    data = {}
    for key, value in get.items():
        data[key] = value[0] if len(value)==1 else value
    return data


