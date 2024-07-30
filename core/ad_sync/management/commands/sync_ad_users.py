# ad_sync/management/commands/sync_ad_users.py

from django.core.management.base import BaseCommand
from django.conf import settings
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from ad_sync.models import ADUser


class Command(BaseCommand):
    help = 'Синхронизация пользователей с Active Directory'

    def handle(self, *args, **kwargs):
        server = Server(settings.LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=settings.LDAP_USER, password=settings.LDAP_PASSWORD, authentication=NTLM)
        if not conn.bind():
            self.stdout.write(self.style.ERROR('Не удалось подключиться к серверу LDAP'))
            return

        conn.search('dc=testorg,dc=com', '(objectClass=person)', SUBTREE,
                    attributes=['cn', 'givenName', 'sn', 'mail', 'userPassword'])

        for entry in conn.entries:
            username = entry.cn.value
            first_name = entry.givenName.value if entry.givenName else ''
            last_name = entry.sn.value if entry.sn else ''
            email = entry.mail.value if entry.mail else ''
            password = entry.userPassword.value if entry.userPassword else ''

            user, created = ADUser.objects.update_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': password,
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'new user is created: {username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'user is updated: {username}'))

        conn.unbind()
