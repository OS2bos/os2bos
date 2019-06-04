from core.models import Case, Municipality, SchoolDistrict


class CaseMixin:
    @staticmethod
    def create_case():
        municipality = Municipality.objects.create(name="København")
        district = SchoolDistrict.objects.create(name="Baltorpskolen")
        case = Case.objects.create(
            sbsys_id="13212",
            cpr_number="0205891234",
            name="Jens Jensen",
            case_worker="Orla Frøsnapper",
            scaling_step=1,
            effort_step="STEP_ONE",
            acting_municipality_id=municipality.id,
            district_id=district.id,
            paying_municipality_id=municipality.id,
            residence_municipality_id=municipality.id,
        )
        return case
