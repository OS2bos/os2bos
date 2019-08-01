"""
This script imports ServiceProviders from the CBUR "Klassifikationer"
spreadsheet.

Currently this requires the sheet "Leverandør" be saved
as "leverandoerer.csv" in the current directory.
"""
import decimal
from decimal import Decimal
from core.models import ServiceProvider
import csv

with open("leverandoerer.csv") as csvfile:
    reader = csv.reader(csvfile)
    models_list = []
    rows = [row for row in reader]
    for row in rows[1:]:
        cvr = row[0]
        name = row[1]
        vat_factor = (
            Decimal(float(row[5][:-1].replace(",", ".")))
            if row[5][:-1]
            else 100.00
        )
        try:
            ServiceProvider.objects.create(
                cvr_number=cvr, name=name, vat_factor=vat_factor
            )
        except decimal.InvalidOperation:
            print(cvr, name, vat_factor)
