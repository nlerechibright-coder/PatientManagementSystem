from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Create hardcoded admin user: godspower'

    def handle(self, *args, **kwargs):
        username = 'godspower'
        password = 'menny12345'
        
        if not CustomUser.objects.filter(username=username).exists():
            CustomUser.objects.create_user(
                username=username,
                email='godspower@hospital.com',
                password=password,
                role='ADMIN',
                is_staff=True,
                is_superuser=False
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))
            self.stdout.write(self.style.WARNING(f'Password: {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))