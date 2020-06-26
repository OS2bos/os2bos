<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="case-edit">
        <form @submit.prevent="saveChanges()">
            
            <header class="case-edit-header">
                <h1 v-if="create_mode">Tilknyt hovedsag</h1>
                <h1 v-else>Redigér hovedsag</h1>
            </header>
            
            <error />

            <div class="row">

                <div class="row-item">
                    <fieldset>
                        <label class="required" for="field-sbsys-id">SBSYS Hovedsag:</label>
                        <input id="field-sbsys-id" type="text" v-model="cas.sbsys_id" required>
                        <p class="danger" v-if="sbsysCheck">Sagsnummeret indeholder ikke et gyldigt KLE-nummer.</p>
                        <error err-key="sbsys_id" />
                    </fieldset>
                    
                    <fieldset>
                        <legend>Sagspart:</legend>
                        <cpr-lookup :cpr.sync="cas.cpr_number" :name.sync="cas.name" :relations.sync="relations"/>
                    </fieldset>
                </div>

                <div class="row-item">
                    <fieldset>
                        <legend>Kommune:</legend>

                        <label class="required" for="selectPayingMunicipality">Betalingskommune:</label>
                        <list-picker 
                            :dom-id="'selectPayingMunicipality'" 
                            :selected-id="cas.paying_municipality" 
                            @selection="changeMuni($event, 'paying_municipality')" 
                            :list="municipalities" 
                            :default="42" />
                    
                        <label class="required" for="selectActingMunicipality">Handlekommune:</label>
                        <list-picker 
                            :dom-id="'selectActingMunicipality'" 
                            :selected-id="cas.acting_municipality" 
                            @selection="changeMuni($event, 'acting_municipality')" 
                            :list="municipalities" 
                            :default="42" />
                    
                        <label class="required" for="selectResidenceMunicipality">Bopælsskommune:</label>
                        <list-picker 
                            :dom-id="'selectResidenceMunicipality'" 
                            :selected-id="cas.residence_municipality" 
                            @selection="changeMuni($event, 'residence_municipality')" 
                            :list="municipalities" 
                            :default="42" />
                    </fieldset>
                </div>

                <div class="row-item">
                    <fieldset>
                        <label class="required" for="selectTargetGroup">Målgruppe:</label>
                        <list-picker
                            :dom-id="'selectTargetGroup'" 
                            :selected-id="cas.target_group" 
                            @selection="changeTargetGroup" 
                            :list="targetGroups" 
                            required />
                        <error err-key="target_group" />
                    
                        <template v-if="requiredDistrict === true">
                            <label class="required" for="selectDistrict">Skoledistrikt (nuværende eller oprindeligt)</label>
                            <list-picker :dom-id="'selectDistrict'" :selected-id="cas.district" @selection="changeDistrict" :list="districts" required />
                        </template>
                    </fieldset>

                    <template v-if="effort_available">
                        <fieldset>
                            <legend style="margin-bottom: .75rem;">Andet:</legend>
                            <template v-for="effort in effort_available">
                                <input 
                                    :key="effort.id"
                                    :id="`inputCheckbox${ effort.id }`" 
                                    type="checkbox" 
                                    :value="effort.id" 
                                    v-model="cas.efforts">
                                <label 
                                    :key="effort.name" 
                                    :for="`inputCheckbox${ effort.id }`">
                                    <span v-if="effort.active === false">(</span>
                                    {{ effort.name }}
                                    <span v-if="effort.active === false">)</span>
                                </label>
                            </template>
                        </fieldset>
                    </template>
                </div>
                
                <div class="row-item" >
                    <fieldset>
                        <legend>Sagsbehandling:</legend>
                        <label for="field-case-info">Supplerende oplysninger for sag</label>
                        <textarea id="field-case-info" v-model="cas.note" placeholder="Angiv supplerende oplysninger her"></textarea>
                        
                        <template v-if="!create_mode">
                            <label class="required" for="selectCaseWorker">Sagsbehandler</label>
                            <list-picker :dom-id="'selectCaseWorker'" :selected-id="cas.case_worker" @selection="changeCaseWorker" :list="users" display-key="fullname" />
                            <dl v-if="cas.team_data">
                                <dt>Team</dt>
                                <dd>{{ cas.team_data.name }}</dd>
                                <dt>Leder</dt>
                                <dd>{{ cas.team_data.leader_name }}</dd>
                            </dl>
                        </template>
                    </fieldset>
                </div>

                <div class="row-item">
                    <assessment-edit :case-obj="cas" @assessment="updateAssessment" />
                </div>

            </div>
            <fieldset class="form-actions">
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>
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
                effort_available: null,
                cas: {
                    efforts: [],
                    target_group: null
                },
                create_mode: true,
                assessment_changes: false,
                relations: null
            }
        },
        computed: {
            municipalities: function() {
                return this.$store.getters.getMunis
            },
            targetGroups: function() {
                return this.$store.getters.getTargetGroups
            },
            districts: function() {
                return this.$store.getters.getDistricts
            },
            efforts: function() {
                return this.$store.getters.getEfforts
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
            },
            requiredDistrict: function() {
                if (this.cas.target_group) {
                    let target = this.targetGroups.filter(tar => tar.id === this.cas.target_group)
                    return target[0].required_fields_for_case.filter(tar => tar === 'district').length === 1
                } else {
                    return false
                }
            }
        },
        watch: {
            cas: {
                handler() {
                    this.fetchEfforts()
                },
                deep: true
            },
        },
        methods: {
            fetchEfforts: function() {
                if (this.cas.target_group) {
                    axios.get(`/efforts/?allowed_for_target_groups=${ this.cas.target_group }`)
                    .then(res => {
                        this.effort_available = res.data    
                    })
                    .catch(err => console.log(err))
                }
            },
            changeMuni: function(ev, type) {
                this.cas[type] = ev
            },
            changeTargetGroup: function(tar) {
                this.cas.target_group = tar
                this.$forceUpdate()
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
                    efforts: this.cas.efforts,
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
            this.fetchEfforts()
            this.$store.commit('clearErrors')
        }
    }
    
</script>

<style>

    .case-edit {
        margin: 1rem 2rem;
    }

    .case-edit form {
        padding: 0;   
    }

    .case-edit .case-edit-header {
        background-color: var(--grey2);
        padding: .5rem 2rem;
    }

    .case-edit .row-item {
        margin: 0;
        padding: 1rem 2rem 2rem;
        border: solid 1px var(--grey2);
    }

    .case-edit .form-actions {
        padding: 2rem;
    }

    .case-button {
        margin-top: 0.5rem;
    }

    .case-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

    .case-edit .listpicker {
        width: auto;
    }

</style>
