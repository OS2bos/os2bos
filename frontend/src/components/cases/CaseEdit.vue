<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="case">
        <form @submit.prevent="saveChanges()">
            
            <h1 v-if="create_mode">Tilknyt hovedsag</h1>
            <h1 v-else>Redigér hovedsag</h1>
            
            <error />
            
            <div class="row">
                <div class="column">
                    <fieldset>
                        <label class="required" for="field-sbsys-id">SBSYS Hovedsag:</label>
                        <input id="field-sbsys-id" type="text" v-model="cas.sbsys_id" required>
                        <p class="danger" v-if="sbsysCheck">Sagsnummeret indeholder ikke et gyldigt KLE-nummer.</p>
                        <error err-key="sbsys_id" />
                    </fieldset>
                    
                    <div>
                        <h3 style="padding-bottom: 0; font-weight: bold; font-size: 1rem;">Sagspart:</h3>
                        <cpr-lookup :cpr.sync="cas.cpr_number" :name.sync="cas.name" />
                    </div>

                    <fieldset>
                        <legend>Kommune:</legend>

                        <label class="required" for="selectField1">Betalingskommune:</label>
                        <list-picker 
                            :dom-id="'selectField1'" 
                            :selected-id="cas.paying_municipality" 
                            @selection="changeMuni($event, 'paying_municipality')" 
                            :list="municipalities" 
                            :default="42" />
                    
                        <label class="required" for="selectField2">Handlekommune:</label>
                        <list-picker 
                            :dom-id="'selectField2'" 
                            :selected-id="cas.acting_municipality" 
                            @selection="changeMuni($event, 'acting_municipality')" 
                            :list="municipalities" 
                            :default="42" />
                    
                        <label class="required" for="selectField3">Bopælsskommune:</label>
                        <list-picker 
                            :dom-id="'selectField3'" 
                            :selected-id="cas.residence_municipality" 
                            @selection="changeMuni($event, 'residence_municipality')" 
                            :list="municipalities" 
                            :default="42" />
                    </fieldset>

                    <fieldset>
                        <legend class="required">Målgruppe:</legend>
                        <input id="inputRadio1" type="radio" value="FAMILY_DEPT" v-model="cas.target_group" name="target-group" required>
                        <label for="inputRadio1">Familieafdelingen</label>
                        <input id="inputRadio2" type="radio" value="DISABILITY_DEPT" v-model="cas.target_group" name="target-group" required>
                        <label for="inputRadio2">Handicapafdelingen</label>
                        <error err-key="target_group" />
                    
                        <template v-if="cas.target_group === 'FAMILY_DEPT'">
                            <label class="required" for="selectField4">Skoledistrikt (nuværende eller oprindeligt)</label>
                            <list-picker :dom-id="'selectField4'" :selected-id="cas.district" @selection="changeDistrict" :list="districts" required />
                        </template>
                    </fieldset>

                    <fieldset>
                        <legend>Andet:</legend>
                        <input id="inputCheckbox1" type="checkbox" v-model="cas.refugee_integration">
                        <label for="inputCheckbox1">Integrationsindsatsen</label>
                        <input id="inputCheckbox2" type="checkbox" v-model="cas.cross_department_measure">
                        <label for="inputCheckbox2">Tværgående ungeindsats</label>
                    </fieldset>

                    <template v-if="!create_mode">
                        <h3>Sagsbehandling:</h3>
                        <fieldset>
                            <label class="required" for="selectCaseWorker">Sagsbehandler</label>
                            <list-picker :dom-id="'selectCaseWorker'" :selected-id="cas.case_worker" @selection="changeCaseWorker" :list="users" display-key="username" />
                        </fieldset>
                        <dl v-if="cas.team_data">
                            <dt>Team</dt>
                            <dd>{{ cas.team_data.name }}</dd>
                            <dt>Leder</dt>
                            <dd>{{ cas.team_data.leader_name }}</dd>
                        </dl>
                    </template>

                    <fieldset>
                        <label for="field-case-info">Supplerende oplysninger for sag</label>
                        <textarea id="field-case-info" v-model="cas.note" placeholder="Angiv supplerende oplysninger her"></textarea>
                    </fieldset>

                    <assessment-edit :case-obj="cas" @assessment="updateAssessment" />
                    
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
    import { userId2name, teamId2name } from '../filters/Labels.js'
    import Error from '../forms/Error.vue'
    import CprLookup from '../forms/CprLookUp.vue'

    export default {

        components: {
            ListPicker,
            AssessmentEdit,
            Error,
            CprLookup
        },
        props: [
            'caseObj'
        ],
        data: function() {
            return {
                cas: {},
                create_mode: true,
                assessment_changes: false
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
            },
            users: function() {
                return this.$store.getters.getUsers
            },
            teams: function() {
                return this.$store.getters.getTeams
            },
            sbsysCheck: function() {
                let kle = this.cas.sbsys_id
                if (kle) {
                    if (!kle.match("27.24.00") && kle.length >= 8) {
                        return true
                    }
                }
            }
        },
        methods: {
            changeMuni: function(ev, type) {
                this.cas[type] = ev
            },
            changeDistrict: function(dist) {
                this.cas.district = dist
            },
            changeCaseWorker: function(user_id) {
                this.cas.case_worker = user_id
                this.fetchTeamInfo()
            },
            fetchTeamInfo: function() {
                if (this.cas.case_worker) {
                    let worker = this.users.find(u => {
                        return u.id === this.cas.case_worker
                    })
                    this.cas.team_data = this.teams.find(t => {
                        return t.id === worker.team
                    })
                    this.cas.team = this.cas.team_data.id
                    this.cas.team_data.leader_name = userId2name(this.cas.team_data.leader)
                    this.$forceUpdate()
                }
            },
            cancel: function() {
                if (!this.create_mode) {
                    this.$emit('close')
                } else {
                    this.$router.push('/')
                }  
            },
            updateAssessment: function(assessment) {
                this.assessment_changes = true
                if (assessment.scaling_step) {
                    this.cas.scaling_step = assessment.scaling_step
                }
                if (assessment.effort_step) {
                    this.cas.effort_step = assessment.effort_step
                }
                if (assessment.assessment_comment) {
                    this.cas.assessment_comment = assessment.assessment_comment
                }
            },
            saveChanges: function() {
                let cpr = this.cas.cpr_number
                let data = {
                    sbsys_id: this.cas.sbsys_id,
                    case_worker: this.cas.case_worker,
                    team: this.cas.team,
                    district: this.cas.district,
                    name: this.cas.name,
                    cpr_number: cpr,
                    paying_municipality: this.cas.paying_municipality,
                    acting_municipality: this.cas.acting_municipality,
                    residence_municipality: this.cas.residence_municipality,
                    target_group: this.cas.target_group,
                    refugee_integration: this.cas.refugee_integration,
                    cross_department_measure: this.cas.cross_department_measure,
                    note: this.cas.note ? this.cas.note : ''
                }
                if (this.assessment_changes) {
                    data.scaling_step = this.cas.scaling_step
                    data.effort_step = this.cas.effort_step
                    data.assessment_comment = this.cas.assessment_comment
                }
                if (!this.create_mode) {
                    axios.patch(`/cases/${ this.cas.id }/`, data)
                    .then(res => {
                        this.$emit('close', res.data)
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                } else {
                    data.case_worker = this.user.id
                    axios.post('/cases/', data)
                    .then(res => {
                        if (this.relations) {
                            for (let i in this.relations) {
                                let r = this.relations[i]
                                let data_related = {
                                    relation_type: r.relation_type,
                                    cpr_number: r.cpr_number,
                                    name: r.name,
                                    related_case: r.related_case ? r.related_case : '',
                                    main_case: res.data.id
                                }
                                axios.post('/related_persons/', data_related)
                                .catch(err => console.log(err))
                            }
                        }
                        this.$router.push(`/case/${ res.data.id }/`)
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                }
            }
        },
        created: function() {
            if (this.caseObj) {
                this.create_mode = false
                this.cas = this.caseObj
                this.fetchTeamInfo()
            }
            this.$store.commit('clearErrors')
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
