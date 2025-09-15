from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or promote a user to admin status'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address of the user to make admin'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='',
            help='First name for the user (if creating new user)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='',
            help='Last name for the user (if creating new user)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the user (if creating new user)'
        )

    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']

        try:
            # Try to get existing user
            user = User.objects.get(email=email)
            self.stdout.write(
                self.style.WARNING(f'User {email} already exists. Promoting to admin...')
            )
        except ObjectDoesNotExist:
            # Create new user
            if not password:
                self.stdout.write(
                    self.style.ERROR('Password is required when creating a new user. Use --password option.')
                )
                return

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created new user: {email}')
            )

        # Make user staff and superuser
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        # Add to admin group if it exists
        try:
            admin_group = Group.objects.get(name='admin')
            user.groups.add(admin_group)
            self.stdout.write(
                self.style.SUCCESS(f'Added {email} to admin group')
            )
        except ObjectDoesNotExist:
            self.stdout.write(
                self.style.WARNING('Admin group does not exist. User is still a superuser.')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully made {email} an admin user!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'User can now access Django admin at /admin/')
        )
