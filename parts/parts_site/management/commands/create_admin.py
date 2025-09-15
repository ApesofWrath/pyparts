from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class Command(BaseCommand):
    help = 'Promote an existing user to admin status'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address of the existing user to make admin'
        )
        parser.add_argument(
            '--create-if-not-exists',
            action='store_true',
            help='Create the user if they do not exist (requires --password)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the user (only needed if creating new user)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='',
            help='First name for the user (only needed if creating new user)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='',
            help='Last name for the user (only needed if creating new user)'
        )

    def handle(self, *args, **options):
        email = options['email']
        create_if_not_exists = options['create_if_not_exists']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        try:
            # Try to get existing user
            user = User.objects.get(email=email)
            self.stdout.write(
                self.style.SUCCESS(f'Found existing user: {email}')
            )
            
            # Check if user is already an admin
            if user.is_superuser and user.is_staff:
                self.stdout.write(
                    self.style.WARNING(f'User {email} is already an admin!')
                )
                return
                
        except ObjectDoesNotExist:
            if not create_if_not_exists:
                self.stdout.write(
                    self.style.ERROR(f'User {email} does not exist. Use --create-if-not-exists to create them.')
                )
                return
            
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
