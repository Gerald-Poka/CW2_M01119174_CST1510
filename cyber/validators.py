import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexPasswordValidator:
    """Require upper, lower, digit and special character (legacy policy)."""

    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('Password must contain at least one lowercase letter.'))
        if not re.search(r'\d', password):
            raise ValidationError(
                _('Password must contain at least one number.'))
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError(
                _('Password must contain at least one special character.'))

    def get_help_text(self):
        return _(
            'Password must contain an uppercase letter, a lowercase letter, '
            'a number and a special character.'
        )
