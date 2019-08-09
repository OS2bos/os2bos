<!-- This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="appropriation" v-if="appr">
        <header class="appropriation-header">
            <div>
                <h1 style="display: inline-block;">Bevillingsskrivelse</h1>
            </div>
            <div>
                <button @click="show_edit = !show_edit" class="appr-edit-btn">Redigér</button>
                <button @click="preApprovalCheck()" class="approval-btn">Godkend</button>
                <approval :approval-obj="appr" v-if="showModal" @close="update()"></approval>
            </div>
        </header>

        <div v-if="show_edit">
            <appropriation-edit :appr-obj="appr" v-if="show_edit" @close="update()" />
        </div>

        <div class="appr-grid" v-if="cas">

            <template v-if="!show_edit">
                <div class="sagsstatus appr-grid-box">
                    <p>
                        <span v-html="statusLabel(appr.status)" style="display: inline-block; margin: .5rem .25rem 0 0;"></span>
                        <template v-if="appr.approval_level"> 
                            af {{ displayApprovalName(appr.approval_level) }}, 
                            {{ displayDate(appr.appropriation_date) }}
                        </template>
                        <span v-if="appr.approval_note && appr.approval_note !== ''">med bemærkningen:<br> <em>{{ appr.approval_note }}</em></span>
                    </p>
                </div>

                <div class="sagsbeh appr-grid-box">
                    <dl>
                        <dt>SBSYS-hovedsag nr.</dt>
                        <dd>{{ cas.sbsys_id }}</dd>
                        <dt>Foranstaltningssag (SBSYS)</dt>
                        <dd>{{ appr.sbsys_id}}</dd>
                        <dt>Sagsbehandler</dt>
                        <dd>{{ displayUserName(cas.case_worker) }}</dd>
                        <template v-if="appr.note">
                            <dt>Supplerende oplysninger</dt>
                            <dd>{{ appr.note }}</dd>
                        </template>
                    </dl>
                </div>

                <div class="sagspart appr-grid-box">
                    <dl>
                        <dt>Sagspart</dt>
                        <dd>{{ cas.cpr_number }}, {{ cas.name }}</dd>
                        <dt>Betalingskommune</dt>
                        <dd>{{ displayMuniName(cas.paying_municipality) }}</dd>
                        <dt>Handlekommune</dt>
                        <dd>{{ displayMuniName(cas.acting_municipality) }}</dd>
                        <dt>Bopælskommune</dt>
                        <dd>{{ displayMuniName(cas.residence_municipality) }}</dd>
                    </dl>
                </div>
                
                <div class="sagslaw appr-grid-box">
                    <dl> 
                        <dt>Bevilges efter §</dt>
                        <dd>{{ displaySection(appr.section) }}</dd>
                    </dl>
                </div>
            </template>

            <div class="sagsbev appr-grid-box">
                <h2>Der bevilges:</h2>
                <activity-list :appr-id="appr.id" />
            </div>

        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'
    import ActivityList2 from '../activities/ActivityList2.vue'
    import ActivityList3 from '../activities/ActivityList3.vue'
    import ActivityList4 from '../activities/ActivityList4.vue'
    import AppropriationEdit from './AppropriationEdit.vue'
    import Approval from './Approval.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { municipalityId2name, districtId2name, sectionId2name, displayStatus, userId2name, approvalId2name } from '../filters/Labels.js'

    export default {

        components: {
            ActivityList,
            ActivityList2,
            ActivityList3,
            ActivityList4,
            AppropriationEdit,
            Approval
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
        watch: {
            appr: function() {
                this.updateBreadCrumb()
            },
            cas: function() {
                this.updateBreadCrumb()
            }
        },
        methods: {
            update: function() {
                this.show_edit =  false
                this.showModal = false
                this.$store.dispatch('fetchAppropriation', this.$route.params.id)
            },
            reload: function() {
                this.show_edit =  false
            },
            displayDate: function(date) {
                return json2jsDate(date)
            },
            preApprovalCheck: function() {
                if (this.appr.activities.length > 0) {
                    this.showModal = true
                } else {
                    alert('Der er ikke valgt nogen aktiviteter endnu')
                }
            },
            updateBreadCrumb: function() {
                if (this.cas && this.appr) {
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/case/${ this.appr.case }`,
                            title: `${ this.cas.sbsys_id }, ${ this.cas.name }`
                        },
                        {
                            link: false,
                            title: `Bevillingsskrivelse ${ this.appr.sbsys_id }`
                        }
                    ])
                }
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
            displayApprovalName: function(id) {
                return approvalId2name(id)
            }
        },
        created: function() {
            this.update()
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
        justify-content: space-between;
    }

    .appropriation-header .material-icons {
        font-size: 3rem;
    }

    .appropriation .appr-edit-btn {
        margin: 0 1rem;
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
