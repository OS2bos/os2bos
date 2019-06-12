from django.contrib.auth import get_user_model

from core.models import Case, Municipality, SchoolDistrict


class CaseMixin:
    @staticmethod
    def create_case():
        case_worker = get_user_model().objects.create(
            username="Orla Frøsnapper"
        )
        municipality = Municipality.objects.create(name="København")
        district = SchoolDistrict.objects.create(name="Baltorpskolen")
        case = Case.objects.create(
            sbsys_id="13212",
            cpr_number="0205891234",
            name="Jens Jensen",
            case_worker=case_worker,
            scaling_step=1,
            effort_step="STEP_ONE",
            acting_municipality=municipality,
            district=district,
            paying_municipality=municipality,
            residence_municipality=municipality,
        )
        return case

    @staticmethod
    def create_case_as_json():
        case_worker = get_user_model().objects.create(username="Andersine And")
        municipality_id = Municipality.objects.create(name="Andeby").id
        district = SchoolDistrict.objects.create(
            name="Kornelius Blisand-skolen"
        )
        json = {
            "sbsys_id": "xxx-yyyx",
            "cpr_number": "111213-0014",
            "name": "Mak Mouse",
            "target_group": "FAMILY_DEPT",
            "refugee_integration": True,
            "cross_department_measure": True,
            "case_worker": case_worker.id,
            "scaling_step": 1,
            "effort_step": "STEP_ONE",
            "district": district.id,
            "paying_municipality": municipality_id,
            "acting_municipality": municipality_id,
            "residence_municipality": municipality_id,
        }

        return json
