<template>
    <section class="case">
        <form @submit.prevent="saveChanges()">
            
            <h1 v-if="create_mode">Tilknyt hovedsag</h1>
            <h1 v-else>Redigér hovedsag</h1>
            
        <div class="row">
            <div class="column">
                <fieldset>
                    <label for="field-sbsys-id">SBSYS Hovedsag:</label>
                    <input id="field-sbsys-id" type="search" v-model="cas.sbsys_id">
                </fieldset>
            
                <fieldset>
                    <label for="field-name">Sagspart, navn</label>
                    <input id="field-name" type="text" v-model="cas.name">
                </fieldset>

                <fieldset>
                    <label for="field-cpr">Sagspart, CPR-nr</label>
                    <input id="field-cpr" type="text" v-model="cas.cpr_number">
                </fieldset>

                <fieldset>
                    <h3>Kommune:</h3>
                    <label for="selectField1">Betalingskommune:</label>
                    <list-picker 
                        :dom-id="'selectField1'" 
                        :selected-id="cas.paying_municipality" 
                        @selection="changeMuni($event, 'paying_municipality')" 
                        :list="municipalities" 
                        default="42" />
                </fieldset>

                <fieldset>
                    <label for="selectField2">Handlekommune:</label>
                    <list-picker 
                        :dom-id="'selectField2'" 
                        :selected-id="cas.acting_municipality" 
                        @selection="changeMuni($event, 'acting_municipality')" 
                        :list="municipalities" 
                        default="42" />
                </fieldset>

                <fieldset>
                    <label for="selectField3">Bopælsskommune:</label>
                    <list-picker 
                        :dom-id="'selectField3'" 
                        :selected-id="cas.residence_municipality" 
                        @selection="changeMuni($event, 'residence_municipality')" 
                        :list="municipalities" 
                        default="42" />
                </fieldset>

                <fieldset>
                    <h3>Målgruppe:</h3>
                    <input id="inputRadio1" type="radio" value="FAMILY_DEPT" v-model="cas.target_group" name="target-group" required>
                    <label for="inputRadio1">Familieafdelingen</label>
                    <input id="inputRadio2" type="radio" value="DISABILITY_DEPT" v-model="cas.target_group" name="target-group" required>
                    <label for="inputRadio2">Handicapafdelingen</label>
                </fieldset>

                <fieldset>
                    <h3>Andet:</h3>
                    <input id="inputCheckbox1" type="checkbox" v-model="cas.refugee_integration">
                    <label for="inputCheckbox1">Integrationsindsatsen</label>
                    <input id="inputCheckbox2" type="checkbox" v-model="cas.cross_department_measure">
                    <label for="inputCheckbox2">Tværgående ungeindsats</label>
                </fieldset>

                <assessment-edit :case-obj="cas" @assessment="updateAssessment" />

                <div>
                    <h3>Sagsbehandling:</h3>
                    <dl>
                        <dt>Sagsbehander:</dt>
                        <dd>{{ cas.case_worker }}</dd>
                        <dt>Team:</dt>
                        <dd>ikke implementeret</dd>
                    </dl>
                    <fieldset v-if="cas.target_group === 'FAMILY_DEPT'">
                        <label for="selectField4">Distrikt:</label>
                        <list-picker :dom-id="'selectField4'" :selected-id="cas.district" @selection="changeDistrict" :list="districts" />
                    </fieldset>
                    <fieldset>
                        <dt>Leder:</dt>
                        <dd>ikke implementeret</dd>
                    </fieldset>
                </div>
                
                <fieldset>
                    <input type="submit" value="Gem">
                    <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
                </fieldset>
            </div>

            <div class="column"></div>
        </div>
        </form>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ListPicker from '../forms/ListPicker.vue'
    import AssessmentEdit from '../assessments/AssessmentEdit.vue'

    export default {

        components: {
            ListPicker,
            AssessmentEdit
        },
        props: [
            'caseObj'
        ],
        data: function() {
            return {
                cas: {},
                create_mode: true
            }
        },
        computed: {
            municipalities: function() {
                return this.$store.getters.getMunis
            },
            districts: function() {
                return this.$store.getters.getDistricts
            },
            user: function() {
                return this.$store.getters.getUser
            }
        },
        methods: {
            changeMuni: function(ev, type) {
                this.cas[type] = ev
            },
            changeDistrict: function(dist) {
                this.cas.district = dist
            },
            cancel: function() {
                if (!this.create_mode) {
                    this.$emit('close')
                } else {
                    this.$router.push('/')
                }  
            },
            updateAssessment: function(assessment) {
                if (assessment.scaling_step) {
                    this.cas.scaling_step = assessment.scaling_step
                }
                if (assessment.effort_step) {
                    this.cas.effort_step = assessment.effort_step
                }
            },
            saveChanges: function() {
                let data = {
                    sbsys_id: this.cas.sbsys_id,
                    case_worker: this.user.id,
                    district: this.cas.district,
                    effort_step: this.cas.effort_step,
                    scaling_step: this.cas.scaling_step,
                    name: this.cas.name,
                    cpr_number: this.cas.cpr_number,
                    paying_municipality: this.cas.paying_municipality,
                    acting_municipality: this.cas.acting_municipality,
                    residence_municipality: this.cas.residence_municipality,
                    target_group: this.cas.target_group,
                    refugee_integration: this.cas.refugee_integration,
                    cross_department_measure: this.cas.cross_department_measure,
                    scaling_step: this.cas.scaling_step,
                    effort_step: this.cas.effort_step
                }
                if (!this.create_mode) {
                    axios.patch(`/cases/${ this.cas.id }/`, data)
                    .then(res => {
                        this.$emit('close', res.data)
                    })
                    .catch(err => console.log(err))
                } else {
                    axios.post('/cases/', data)
                    .then(res => {
                        this.$router.push(`/case/${ res.data.id }/`)
                    })
                    .catch(err => console.log(err))
                }
            }
        },
        created: function() {
            if (this.caseObj) {
                this.create_mode = false
                this.cas = this.caseObj
            }
        }
    }
    
</script>

<style>

    .case {
        margin: 1rem;
    }

    .case-button {
        margin-top: 0.5rem;
    }

    .case .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>