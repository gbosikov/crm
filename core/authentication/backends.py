# auth_app/backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from ldap3 import Server, Connection, NTLM
from Crypto.Hash import MD4


class ActiveDirectoryBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        domain_username = f"{settings.LDAP_DOMAIN}\\{username}"
        server = Server(settings.LDAP_SERVER)
        conn = Connection(server, user=domain_username, password=password, authentication=NTLM)

        if conn.bind():
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Создаем нового пользователя в Django, если его еще нет
                user = User(username=username)
                user.set_unusable_password()
                user.save()
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
