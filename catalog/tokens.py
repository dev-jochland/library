import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UserTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        user_id = six.text_type(user.pk)
        ts = six.text_type(timestamp)
        is_active = six.text_type(user.is_active)
        return '{}{}{}'.format(user_id, ts, is_active)


user_tokenizer = UserTokenGenerator()
