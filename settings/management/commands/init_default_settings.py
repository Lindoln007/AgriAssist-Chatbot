"""
Management command to initialize default settings for all users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from settings.utils import ensure_all_default_settings


class Command(BaseCommand):
    help = 'Initialize default settings for all existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Initialize settings for a specific user (username)',
        )

    def handle(self, *args, **options):
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                ensure_all_default_settings(user)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully initialized settings for user: {user.username}')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{options["user"]}" not found')
                )
        else:
            # Initialize for all users
            users = User.objects.all()
            count = 0
            for user in users:
                ensure_all_default_settings(user)
                count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully initialized settings for {count} user(s)')
            )

