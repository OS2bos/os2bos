<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="appropriation" v-if="appr">
        <header class="appropriation-header">
            <h1 style="display: inline-block;">
                <i class="material-icons">folder_open</i>
                Bevillingsskrivelse
            </h1>
            <button v-if="user_can_edit === true && !show_edit" @click="show_edit = !show_edit" class="appr-edit-btn">Redigér</button>
            <button v-if="appr.num_ongoing_activities === 0 && !show_edit" class="appr-delete-btn" @click="preDeleteCheck()">Slet</button>
        </header>

        <appropriation-edit :appr-obj="appr" v-if="show_edit" @close="update()" />

        <!-- Delete activity modal -->
        <div v-if="showModal">
            <form @submit.prevent="deleteAppr(appr.id)" class="modal-form">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div class="modal-container">

                            <div class="modal-header">
                                <slot name="header">
                                    <h2>Slet</h2>
                                </slot>
                            </div>

                            <div class="modal-body">
                                <slot name="body">
                                    <p>
                                        Er du sikker på, at du vil slette denne bevillingsskrivelse?
                                    </p>
                                </slot>
                            </div>

                            <div class="modal-footer">
                                <slot name="footer">
                                    <button type="button" class="modal-cancel-btn" @click="cancel">Annullér</button>
                                    <button class="modal-delete-btn" type="submit">Slet</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <div class="appr-grid" v-if="cas">

            <template v-if="!show_edit">

                <div class="sagsbeh appr-grid-box">
                    <dl>
                        <dt>Foranstaltningssag</dt>
                        <dd>{{ appr.sbsys_id}}</dd>
                        <dt>SBSYS-hovedsag</dt>
                        <dd>{{ cas.sbsys_id }}</dd>
                        <dt>Sagspart (CPR, navn)</dt>
                        <dd>
                            {{ cas.cpr_number }}<br>
                            {{ cas.name }}
                        </dd>
                        <template v-if="appr.note">
                            <dt>Supplerende oplysninger</dt>
                            <dd>{{ appr.note }}</dd>
                        </template>
                    </dl>
                </div>

                <div class="sagspart appr-grid-box">
                    <dl>
                        <dt>Sagsbehandler</dt>
                        <dd>{{ displayUserName(cas.case_worker) }}</dd>
                        <dt>Betalingskommune</dt>
                        <dd>{{ cas.paying_municipality }}</dd>
                        <dt>Handlekommune</dt>
                        <dd>{{ cas.acting_municipality }}</dd>
                        <dt>Bopælskommune</dt>
                        <dd>{{ cas.residence_municipality }}</dd>
                    </dl>
                </div>
                
                <div class="sagslaw appr-grid-box">
                    <dl> 
                        <dt>Bevilges efter §</dt>
                        <dd v-html="displaySection(appr.section)"></dd>
                    </dl>
                </div>
            </template>

            <div class="sagsbev appr-grid-box">
                <activity-list :appr-id="$route.params.apprId" />
            </div>

        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'
    import AppropriationEdit from './AppropriationEdit.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { municipalityId2name, districtId2name, sectionId2name, displayStatus, userId2name } from '../filters/Labels.js'
    import PermissionLogic from '../mixins/PermissionLogic.js'
    import notify from '../notifications/Notify.js'

    export default {

        mixins: [
            PermissionLogic
        ],
        components: {
            ActivityList,
            AppropriationEdit
        },
        data: function() {
            return {
                show_edit: false,
                showModal: false
            }
        },
        computed: {
            cas: function() {
                return this.$store.getters.getCase
            },
            appr: function() {
                return this.$store.getters.getAppropriation
            }
        },
        methods: {
            update: function(appropriation_id) {
                this.show_edit =  false
                this.showModal = false
                this.fetchApprData(appropriation_id)
            },
            displayDate: function(date) {
                return json2jsDate(date)
            },
            updateBreadCrumb: function(appr_data, case_data) {
                this.$store.commit('setBreadcrumb', [
                    {
                        link: '/',
                        title: 'Sager'
                    },
                    {
                        link: `/case/${ case_data.id }`,
                        title: `${ case_data.sbsys_id }, ${ case_data.name }`
                    },
                    {
                        link: false,
                        title: `Bevillingsskrivelse ${ appr_data.sbsys_id }`
                    }
                ])
            },
            displayMuniName: function(id) {
                return municipalityId2name(id)
            },
            displayDistrictName: function(id) {
                return districtId2name(id)
            },
            displaySection: function(id) {
                return sectionId2name(id)
            },
            statusLabel: function(status) {
                return displayStatus(status)
            },
            displayUserName: function(id) {
                return userId2name(id)
            },
            preDeleteCheck: function() {
                this.showModal = true
            },
            cancel: function() {
                this.showModal = false
            },
            deleteAppr: function(appr_id) {
                axios.delete(`/appropriations/${ appr_id }/`)
                .then(() => {
                    this.$router.push(`/case/${ this.cas.id }`)
                    notify('Bevillingsskrivelse slettet', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            },
            fetchApprData: function(appropriation_id) {
                // TODO: get data for appropriation section
                const id = btoa(`Appropriation:${appropriation_id}`)
                let data = {
                    query: `{
                        appropriation(id: "${ id }") {
                            pk,
                            sbsysId,
                            note,
                            case {
                                pk,
                                sbsysId,
                                name,
                                cprNumber,
                                caseWorker {
                                    pk
                                },
                                payingMunicipality {
                                    name
                                },
                                actingMunicipality {
                                    name
                                },
                                residenceMunicipality {
                                    name
                                },
                                targetGroup {
                                    pk
                                },
                                effortStep {
                                    pk
                                }
                            },
                            section {
                                pk
                            }
                            activities {
                                edges {
                                    node {
                                        pk,
                                        activityType,
                                        startDate,
                                        endDate,
                                        status,
                                        details {
                                            pk
                                        },
                                        modifies {
                                            pk
                                        }
                                    }
                                }
                            }
                        }
                    }`
                }
                axios.post('/graphql/', data)
                .then(res => {
                    if (!res.data.data.appropriation) {
                        return false
                    }
                    const a = res.data.data.appropriation
                    const new_appr = {
                        id: a.pk,
                        case: a.case.pk,
                        sbsys_id: a.sbsysId,
                        note: a.note,
                        section: a.section.pk,
                        activities: [...a.activities.edges.map(e => {
                            return {
                                id: Number(e.node.pk),
                                activity_type: e.node.activityType,
                                start_date: e.node.startDate,
                                end_date: e.node.endDate,
                                details: Number(e.node.details.pk),
                                modifies: e.node.modifies ? e.node.modifies.pk : null
                            }
                        })],
                        num_ongoing_activities: a.activities.edges.length,
                        granted: this.getGrantedActStatus(a.activities.edges)
                    }
                    const new_case = {
                        name: a.case.name,
                        id: a.case.pk,
                        sbsys_id: a.case.sbsysId,
                        cpr_number: a.case.cprNumber,
                        case_worker: a.case.caseWorker.pk,
                        residence_municipality: a.case.residenceMunicipality.name,
                        paying_municipality: a.case.payingMunicipality.name,
                        acting_municipality: a.case.actingMunicipality.name,
                        target_group: a.case.targetGroup.pk,
                        effort_step: a.case.effortStep.pk
                    }
                    this.$store.dispatch("fetchMainActivities", new_appr.activities)
                    this.$store.commit('setAppropriation', new_appr)
                    this.$store.commit('setCase', new_case)
                    this.updateBreadCrumb(new_appr, new_case)
                })
                .catch(err => {
                    console.error('Error fetching Appropriation data', err)
                    this.$store.commit('setAppropriation', null)
                })
            },
            getGrantedActStatus: function(activities) {
                const granted_act = activities.find(function(edge) {
                    return edge.node.status === 'GRANTED'
                })
                return granted_act ? true : false
            }
            
        },
        beforeRouteUpdate: function(to, from, next) {
            this.update(to.params.apprId)
            next()
        },
        created: function() {
            this.update(this.$route.params.apprId)
        }
    }
    
</script>

<style>

    .appropriation {
        margin: 1rem 2rem 2rem;
    }

    .appropriation-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .appropriation .appropriation-edit {
        width: auto;
        margin: 1rem 0 2rem;
    }

    .appropriation-header .material-icons {
        font-size: 3rem;
    }

    .appropriation .appr-edit-btn {
        margin: 0 1rem;
    }

    .appropriation .appr-delete-btn,
    .appropriation .modal-delete-btn {
        margin: 0;
        border-color: var(--danger);
        color: var(--danger);
        background-color: transparent;
    }
    .modal-delete-btn {
        float: right;
        margin-left: 0.5rem;
    }

    .appropriation .appr-delete-btn:focus,
    .appropriation .appr-delete-btn:hover,
    .appropriation .appr-delete-btn:active,
    .modal-delete-btn:focus,
    .modal-delete-btn:hover,
    .modal-delete-btn:active {
        background-color: var(--danger);
        color: var(--grey0);
        border-color: var(--danger);
    }

    .appropriation .approval-btn {
        margin: 0 1rem;
    }

    .appropriation .status-Godkendt {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

    .appr-grid {
        display: grid;
        grid-template-columns: repeat(6, auto);
        grid-template-rows: repeat(4, auto);
    }

    .appr-grid-box {
        border: solid 1px var(--grey1);
        padding: .5rem 1rem;
        margin: 1px;
    }

    .sagsstatus {
        grid-area: 1 / 1 / 2 / 7;
    }

    .sagsbeh {
        grid-area: 2 / 1 / 3 / 4;
    }

    .sagspart {
        grid-area: 2 / 4 / 3 / 7;
    }

    .sagslaw {
        grid-area: 3 / 1 / 4 / 7;
        background-color: var(--grey1);
    }

    .sagsbev {
        grid-area: 4 / 1 / 5 / 7;
    }

    @media screen and (min-width: 45rem) {
        
        .appropriation .appr-header {
            display: grid;
            grid-gap: 0 2rem;
            grid-template-columns: 1fr 1fr;
        }

    }

</style>
