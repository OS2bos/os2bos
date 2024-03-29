# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Functions for populating the database with initial data."""

from django.core.management import call_command

from core.data.municipalities import municipalities
from core.data.school_districts import school_districts
from core.data.teams import teams
from core.models import Municipality, SchoolDistrict, Team, User


def initialize():
    """Initialize all the basic data we want at start.

    Should be able to be run multiple times over without generating duplicates.
    """
    initialize_municipalities()
    initialize_school_districts()
    initialize_target_groups()
    initialize_sections()
    initialize_activity_details()
    initialize_activity_categories()
    initialize_section_infos()
    initialize_service_providers()
    initialize_users()
    initialize_teams()
    initialize_approval_levels()
    initialize_payment_method_details()
    initialize_rates()
    initialize_account_alias_mappings()


def initialize_municipalities():
    """Initialize all the danish municipalities."""
    for name in municipalities:
        Municipality.objects.get_or_create(name=name)


def initialize_approval_levels():
    """Initialize all the initial approval levels.

    Data should be the output of "manage.py dumpdata core.approvallevels".
    """
    call_command("loaddata", "approvallevels.json", app_label="core")


def initialize_target_groups():
    """Initialize the initial target groups.

    Data should be output of "manage.py dumpdata core.targetgroups".
    """
    call_command("loaddata", "targetgroups.json", app_label="core")


def initialize_sections():
    """Initialize all the relevant law sections.

    Data should be the output of "manage.py dumpdata core.section".
    """
    call_command("loaddata", "sections.json", app_label="core")


def initialize_activity_details():
    """Initialize all the relevant activity details.

    Data should be the output of "manage.py dumpdata core.activitydetails".

    """
    call_command("loaddata", "activitydetails.json", app_label="core")


def initialize_section_infos():
    """Initialize all the relevant section infos.

    Data should be the output of "manage.py dumpdata core.sectioninfos".

    """
    call_command("loaddata", "sectioninfos.json", app_label="core")


def initialize_activity_categories():
    """Initialize all the relevant activity categories.

    Data should be the output of "manage.py dumpdata core.activitycategory
    """
    call_command("loaddata", "activity_categories.json", app_label="core")


def initialize_service_providers():
    """Initialize all the relevant service providers.

    Data should be the output of "manage.py dumpdata core.serviceprovider".
    """
    call_command("loaddata", "serviceproviders.json", app_label="core")


def initialize_users():
    """Prime the system with some users to get started.

    Data should be the output of "manage.py dumpdata core.User".

    """
    call_command("loaddata", "users.json", app_label="core")


def initialize_payment_method_details():
    """Initialize all the relevant payment method details."""
    call_command("loaddata", "paymentmethoddetails.json", app_label="core")


def initialize_school_districts():
    """Initialize all the school districts for Ballerup."""
    for name in school_districts:
        SchoolDistrict.objects.get_or_create(name=name)


def initialize_teams():
    """Initialize all the school districts for Ballerup."""
    for (name, team_leader, members) in teams:
        leader = User.objects.get(username=team_leader)
        team, _ = Team.objects.get_or_create(name=name, leader=leader)
        for name in members:
            user = User.objects.get(username=name)
            user.team = team
            user.save()


def initialize_rates():
    """Initialize the variable rates, rates and rates per date for Ballerup."""
    call_command("loaddata", "variablerates.json", app_label="core")
    call_command("loaddata", "rates.json", app_label="core")
    call_command("loaddata", "ratesperdate.json", app_label="core")


def initialize_account_alias_mappings():
    """Initialize the account alias mappings."""
    call_command("loaddata", "accountaliasmappings.json", app_label="core")
