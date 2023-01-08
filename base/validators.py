import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(_("The password must contain at least 1 digit."), code='password_no_number')

    def get_help_text(self):
        return _("Your password must contain at least 1 digit.")
