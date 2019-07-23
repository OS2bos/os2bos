import sys
from django.core.management.base import BaseCommand

from bevillingsplatform.initialize import initialize


class Command(BaseCommand):
    """
    Initialize database.
    Helper command to seed database with (static) basic data.

    :Reference: :mod:`bevillingsplatform.initialize`

    Should be able to be run multiple times over without generating duplicates.

    Example:

        $ python manage.py initialize_database

    """

    help = "Call initialize function to seed the database"

    def handle(self, *args, **options):

        # Display action
        print("Seed database with (static) basic data")

        # Run script
        initialize()

        # Inform user that the operation is complete
        # Assuming that if any of the underlying functions fail
        # the process is stopped/caught in place
        print("Database seeded with (static) basic data")

        # Exit clean
        sys.exit(0)
