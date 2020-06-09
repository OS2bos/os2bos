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
            <button v-if="permissionCheck === true" @click="show_edit = !show_edit" class="appr-edit-btn">Redigér</button>
            <button v-if="appr.status === 'DRAFT'" class="appr-delete-btn" @click="preDeleteCheck()">Slet</button>
        </header>

        <appropriation-edit :appr-obj="appr" v-if="show_edit" @close="update()" />

        <!-- Delete activity modal -->
        <div v-if="showModal">
            <form @submit.prevent="deleteAppr()" class="modal-form">
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
                                        Er du sikker på, at du vil slette denne kladde?
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
                        <dd>{{ cas.cpr_number }}, {{ cas.name }}</dd>
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
                        <dd v-html="displayMuniName(cas.paying_municipality)"></dd>
                        <dt>Handlekommune</dt>
                        <dd v-html="displayMuniName(cas.acting_municipality)"></dd>
                        <dt>Bopælskommune</dt>
                        <dd v-html="displayMuniName(cas.residence_municipality)"></dd>
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
                <activity-list :appr-id="appr.id" />
            </div>

        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'
    import AppropriationEdit from './AppropriationEdit.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { municipalityId2name, districtId2name, sectionId2name, displayStatus, userId2name, approvalId2name } from '../filters/Labels.js'
    import store from '../../store.js'
    import UserRights from '../mixins/UserRights.js'
    import notify from '../notifications/Notify.js'

    export default {

        mixins: [UserRights],

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
        beforeRouteEnter: function(to, from, next) {
            store.commit('clearAppropriation')
            store.dispatch('fetchAppropriation', to.params.apprId)
            .then(() => next())
        },
        beforeRouteUpdate: function(to, from, next) {
            store.dispatch('fetchAppropriation', to.params.apprId)
            .then(() => next())
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
                this.$store.dispatch('fetchAppropriation', this.$route.params.apprId)
            },
            displayDate: function(date) {
                return json2jsDate(date)
            },
            updateBreadCrumb: function() {
                if (this.cas && this.appr) {
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Sager'
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
            preDeleteCheck: function() {
                this.showModal = true
            },
            cancel: function() {
                this.showModal = false
            },
            deleteAppr: function() {
                axios.delete(`/appropriations/${ this.appr.id }/`)
                .then(res => {
                    this.$router.push(`/case/${ this.cas.id }`)
                    notify('Bevillings kladde slettet', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            },
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
    .modal-delete-btn {
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
