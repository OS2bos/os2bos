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
        try:
            initialize()
        except Exception as error:
            print(
                "!! ERROR running the script - See python traceback output !!"
            )
            print(error)

            # Exit unclean
            sys.exit(1)

        # Exit clean
        sys.exit(0)
