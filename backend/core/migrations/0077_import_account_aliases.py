import os
import csv

from django.db import migrations
from django.db.models import Q


def import_account_aliases(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [("core", "0076_auto_20200629_1154")]

    operations = [migrations.RunPython(import_account_aliases)]
