from django.db import migrations

from core.models import Section, SectionInfo, ActivityDetails

def forwards(apps, schema_editor):
    """Reload the section -> main_activities link corresponding to fixtures.

    When fixtures change/new spreadsheets are supplied, this migration
    must be regenerated. This can be done by printing out the
    ``update_or_create`` statements from the file
    ``scripts/import_activity_details``.
    """

    # If database hasn't been initialized, do nothing.

    if not ActivityDetails.objects.filter(pk=1661).exists():
        return

    # Clear existing to avoid duplicate keys.
    for section in Section.objects.all():
        section.main_activities.clear()

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1661),
            section=Section.objects.get(pk=1043),
            kle_number='27.24.09',
            sbsys_template_id='1592',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1708),
            section=Section.objects.get(pk=1030),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1708),
            section=Section.objects.get(pk=1028),
            kle_number='27.24.03',
            sbsys_template_id='1561',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1709),
            section=Section.objects.get(pk=1035),
            kle_number='27.27.09',
            sbsys_template_id='1296',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1704),
            section=Section.objects.get(pk=1026),
            kle_number='27.36.08',
            sbsys_template_id='972',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1712),
            section=Section.objects.get(pk=1036),
            kle_number='27.27.12',
            sbsys_template_id='886',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1716),
            section=Section.objects.get(pk=1042),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1716),
            section=Section.objects.get(pk=1043),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1717),
            section=Section.objects.get(pk=1033),
            kle_number='27.27.03',
            sbsys_template_id='899',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1713),
            section=Section.objects.get(pk=1030),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1713),
            section=Section.objects.get(pk=1028),
            kle_number='27.24.03',
            sbsys_template_id='1562',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1697),
            section=Section.objects.get(pk=1025),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1698),
            section=Section.objects.get(pk=1022),
            kle_number='27.18.24',
            sbsys_template_id='921',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1657),
            section=Section.objects.get(pk=1075),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1662),
            section=Section.objects.get(pk=1043),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1669),
            section=Section.objects.get(pk=1023),
            kle_number='32.18.04',
            sbsys_template_id='914',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1642),
            section=Section.objects.get(pk=994),
            kle_number='27.12.08',
            sbsys_template_id='1556',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1674),
            section=Section.objects.get(pk=1060),
            kle_number='27.27.32',
            sbsys_template_id='877',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1674),
            section=Section.objects.get(pk=1080),
            kle_number='',
            sbsys_template_id=' ',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1674),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1578',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1674),
            section=Section.objects.get(pk=1037),
            kle_number='27.27.15',
            sbsys_template_id='1565',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1674),
            section=Section.objects.get(pk=1026),
            kle_number='27.21.16',
            sbsys_template_id='1557',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1674),
            section=Section.objects.get(pk=1039),
            kle_number='27.27.32',
            sbsys_template_id='877',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1671),
            section=Section.objects.get(pk=1024),
            kle_number='32.18.12',
            sbsys_template_id='916',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1638),
            section=Section.objects.get(pk=1042),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1638),
            section=Section.objects.get(pk=1044),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1714),
            section=Section.objects.get(pk=1016),
            kle_number='27.18.02',
            sbsys_template_id='920',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1718),
            section=Section.objects.get(pk=1071),
            kle_number='27.24.00',
            sbsys_template_id='887',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1653),
            section=Section.objects.get(pk=1042),
            kle_number='27.24.09',
            sbsys_template_id='1590',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1653),
            section=Section.objects.get(pk=1043),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1653),
            section=Section.objects.get(pk=1044),
            kle_number='27.24.09',
            sbsys_template_id='1594',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1705),
            section=Section.objects.get(pk=1041),
            kle_number='27.27.54',
            sbsys_template_id='884',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1710),
            section=Section.objects.get(pk=1026),
            kle_number='27.21.16',
            sbsys_template_id='1554',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1710),
            section=Section.objects.get(pk=1060),
            kle_number='27.27.45',
            sbsys_template_id='1568',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1710),
            section=Section.objects.get(pk=1037),
            kle_number='27.27.15',
            sbsys_template_id='1595',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1711),
            section=Section.objects.get(pk=1026),
            kle_number='27.26.16',
            sbsys_template_id='1555',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1711),
            section=Section.objects.get(pk=1060),
            kle_number='27.27.27',
            sbsys_template_id='1569',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1711),
            section=Section.objects.get(pk=1037),
            kle_number='27.27.15',
            sbsys_template_id='1564',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1711),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1576',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1715),
            section=Section.objects.get(pk=1027),
            kle_number='27.21.08',
            sbsys_template_id='911',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1719),
            section=Section.objects.get(pk=1034),
            kle_number='27.27.06',
            sbsys_template_id='900',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1654),
            section=Section.objects.get(pk=1045),
            kle_number='27.24.15',
            sbsys_template_id='903',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1658),
            section=Section.objects.get(pk=1075),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1699),
            section=Section.objects.get(pk=1047),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1643),
            section=Section.objects.get(pk=1060),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1643),
            section=Section.objects.get(pk=1080),
            kle_number='',
            sbsys_template_id=' ',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1643),
            section=Section.objects.get(pk=1075),
            kle_number='27.27.00',
            sbsys_template_id='1588',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1643),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1581',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1643),
            section=Section.objects.get(pk=1039),
            kle_number='27.27.42',
            sbsys_template_id='882',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1060),
            kle_number='27.27.39',
            sbsys_template_id='881',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1080),
            kle_number='',
            sbsys_template_id=' ',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1075),
            kle_number='',
            sbsys_template_id='1599',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1042),
            kle_number='27.24.09',
            sbsys_template_id='1591',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1043),
            kle_number='27.24.09',
            sbsys_template_id='1593',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1600',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1644),
            section=Section.objects.get(pk=1039),
            kle_number='27.27.39',
            sbsys_template_id='881',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1655),
            section=Section.objects.get(pk=1040),
            kle_number='27.27.51',
            sbsys_template_id='896',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1720),
            section=Section.objects.get(pk=972),
            kle_number='27.57.12',
            sbsys_template_id='1552',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1652),
            section=Section.objects.get(pk=991),
            kle_number='27.12.06',
            sbsys_template_id='999',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1659),
            section=Section.objects.get(pk=1075),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1666),
            section=Section.objects.get(pk=1060),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1666),
            section=Section.objects.get(pk=1080),
            kle_number='',
            sbsys_template_id=' ',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1666),
            section=Section.objects.get(pk=1039),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1648),
            section=Section.objects.get(pk=1078),
            kle_number='27.27.00',
            sbsys_template_id='1589',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1648),
            section=Section.objects.get(pk=1043),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1648),
            section=Section.objects.get(pk=1074),
            kle_number='27.24.00',
            sbsys_template_id='889',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1648),
            section=Section.objects.get(pk=1038),
            kle_number='27.27.24',
            sbsys_template_id='895',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1645),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1577',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1645),
            section=Section.objects.get(pk=1039),
            kle_number='27.27.36',
            sbsys_template_id='880',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1706),
            section=Section.objects.get(pk=1076),
            kle_number='27.24.00',
            sbsys_template_id='891',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1702),
            section=Section.objects.get(pk=987),
            kle_number='27.27.07',
            sbsys_template_id='997',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1667),
            section=Section.objects.get(pk=972),
            kle_number='27.57.12',
            sbsys_template_id='922',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1703),
            section=Section.objects.get(pk=982),
            kle_number='27.12.06',
            sbsys_template_id='996',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1656),
            section=Section.objects.get(pk=1075),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1649),
            section=Section.objects.get(pk=1038),
            kle_number='27.27.21',
            sbsys_template_id='893',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1721),
            section=Section.objects.get(pk=1089),
            kle_number='',
            sbsys_template_id='',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1646),
            section=Section.objects.get(pk=1035),
            kle_number='27.27.09',
            sbsys_template_id='894',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1707),
            section=Section.objects.get(pk=1029),
            kle_number='27.24.03',
            sbsys_template_id='1560',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1650),
            section=Section.objects.get(pk=981),
            kle_number='27.12.06',
            sbsys_template_id='997',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1060),
            kle_number='27.27.30',
            sbsys_template_id='879',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1081),
            kle_number='27.24.00',
            sbsys_template_id='892',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1080),
            kle_number='',
            sbsys_template_id=' ',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1580',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1075),
            kle_number='27.27.00',
            sbsys_template_id='1587',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1037),
            kle_number='27.27.15',
            sbsys_template_id='1567',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1026),
            kle_number='27.21.16',
            sbsys_template_id='1559',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1036),
            kle_number='27.27.12',
            sbsys_template_id='1563',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1664),
            section=Section.objects.get(pk=1039),
            kle_number='27.27.30',
            sbsys_template_id='879',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1060),
            kle_number='27.27.33',
            sbsys_template_id='878',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1080),
            kle_number='',
            sbsys_template_id=' ',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1073),
            kle_number='27.27.00',
            sbsys_template_id='1579',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1075),
            kle_number='27.27.00',
            sbsys_template_id='1586',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1037),
            kle_number='27.27.15',
            sbsys_template_id='1566',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1026),
            kle_number='27.21.16',
            sbsys_template_id='1558',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1665),
            section=Section.objects.get(pk=1039),
            kle_number='27.27.33',
            sbsys_template_id='878',)

    SectionInfo.objects.update_or_create(
            activity_details=ActivityDetails.objects.get(pk=1651),
            section=Section.objects.get(pk=989),
            kle_number='27.12.06',
            sbsys_template_id='998',)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20190906_1541')
    ]

    operations = [
        migrations.RunPython(forwards)
    ]
