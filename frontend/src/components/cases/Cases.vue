<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>


    <div class="case-search">
        <div class="case-search-filters">
            <h2 class="case-search-filters--title">Filtrér sager</h2>
            <form @submit.prevent>
                <ul class="filter-fields">
                    <li>
                        <label for="field-sbsysid">SBSYS ID</label>
                        <input type="search" @input="update()" id="field-sbsysid" v-model="$route.query.sbsys_id">
                    </li>

                    <li>
                        <label for="field-cpr">CPR-nr</label>
                        <input type="search" @input="changeCpr" id="field-cpr" v-model="$route.query.cpr_number">
                    </li>

                    <li>
                        <label for="field-team">Team</label>
                        <list-picker 
                            v-if="teams"
                            :dom-id="'field-team'" 
                            :selected-id="query.team"
                            :list="teams"
                            @selection="changeTeam"
                            display-key="name" />
                    </li>

                    <li>
                        <label for="field-case-worker">Sagsbehandler</label>
                        <list-picker 
                            v-if="users"
                            :dom-id="'field-case-worker'" 
                            :selected-id="query.case_worker"
                            :list="users"
                            @selection="changeWorker"
                            display-key="fullname" />
                    </li>
                </ul>

                <ul class="filter-fields">
                    <li>
                        <input type="radio" v-model="$route.query.expired" id="field-expired-1" @change="update()" :value="null">
                        <label for="field-expired-1">Aktive og lukkede sager</label>
                    </li>
                    <li>
                        <input type="radio" v-model="$route.query.expired" id="field-expired-2" @change="update()" :value="false">
                        <label for="field-expired-2">Kun aktive sager</label>
                    </li>
                    <li>
                        <input type="radio" v-model="$route.query.expired" id="field-expired-3" @change="update()" :value="true">
                        <label for="field-expired-3">Kun lukkede sager</label>
                    </li>
                </ul>
            </form>
        </div>
        
        <div class="case-search-list">

            <data-grid v-if="cases"
                       ref="data-grid"
                       :data-list="cases"
                       :columns="columns"
                       @selection="updateSelectedCases"
                       :selectable="permissionCheck">

                <div slot="datagrid-header">
                    <h1 style="padding: 0;">Sager</h1>
                    <button v-if="permissionCheck === true" class="create" @click="$router.push('/case-create/')">+ Tilknyt hovedsag</button>
                </div>
                <p slot="datagrid-footer" v-if="cases.length < 1">
                    Kan ikke finde nogen resultater, der matcher de valgte kriterier
                </p>

            </data-grid>

            <button v-if="cases.length > 0 && permissionCheck"
                    :disabled="selected_cases.length < 1" 
                    class="case-search-move-btn"
                    @click="show_modal = true">
                <i class="material-icons">forward</i>
                Flyt sager
            </button>            

            <dialog-box v-if="show_modal">
                <div slot="header">
                    <h2>Flyt sager til en medarbejder</h2>
                </div>
                <div slot="body">
                    <div class="row" style="justify-content: space-between;">
                        <div class="move-cases-list">
                            <p>Sager, der vil blive flyttet:</p>
                            <ul>
                                <li v-for="c in selected_cases" :key="c.id">
                                    Hovedsag {{ c.sbsys_id }}
                                </li>
                            </ul>
                        </div>
                        <fieldset class="move-cases-field">
                            <label for="diag-field-case-worker">Vælg medarbejder</label>
                            <list-picker 
                                :dom-id="'diag-field-case-worker'"
                                :list="users"
                                @selection="diagChangeWorker"
                                display-key="fullname" />
                        </fieldset>
                    </div>
                </div>
                <div slot="footer">
                    <button @click="moveCases()">Flyt</button>
                    <button @click="closeMoveDiag()" class="modal-cancel-btn">Annuller</button>
                </div>
            </dialog-box>

        </div>
    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import { json2js } from '../filters/Date.js'
    import ListPicker from '../forms/ListPicker.vue'
    import DialogBox from '../dialog/Dialog.vue'
    import notify from '../notifications/Notify.js'
    import CaseFilters from '../mixins/CaseFilters.js'
    import UserRights from '../mixins/UserRights.js'
    import { targetGroupId2name, districtId2name, displayEffort, userId2name, teamId2name } from '../filters/Labels.js'

    export default {

        components: {
            DataGrid,
            ListPicker,
            DialogBox
        },
        mixins: [
            CaseFilters,
            UserRights
        ],
        data: function() {
            return {
                preselected: null,
                selected_cases: [],
                show_modal: false,
                diag_field_case_worker: null,
                columns: [
                    {
                        key: 'expired',
                        title: 'Status',
                        display_func: this.displayStatus,
                        class: 'datagrid-td-status'
                    },
                    {
                        key: 'sbsys_id',
                        title: 'SBSYS ID',
                        display_func: this.displayID,
                        class: 'datagrid-action'
                    },
                    {
                        key: 'cpr_number',
                        title: 'CPR/Navn',
                        display_func: this.displayCPRName
                    },
                    {
                        key: 'target_group',
                        title: 'Målgruppe',
                        display_func: this.displayTargetGroupDistrict,
                        class: 'nowrap'
                    },
                    {
                        key: 'effort_step',
                        title: 'Indsatstrappen',
                        display_func: this.displayEffortName
                    },
                    {
                        key: 'num_appropriations',
                        title: 'Bevillinger',
                        display_func: this.displayAppr,
                        class: 'nowrap'
                    },
                    {
                        key: 'case_worker',
                        title: 'Sagsbehandler',
                        display_func: this.displayUserTeam
                    },
                    {
                        key: 'modified',
                        title: 'Ændret',
                        display_func: this.displayDate
                    }
                ]
            }
        },  
        computed: {
            cases: function() {
                return this.$store.getters.getCases
            },
            users: function() {
                return this.$store.getters.getUsers
            },
            teams: function() {
                return this.$store.getters.getTeams
            },
            user: function() {
                let user = this.$store.getters.getUser
                if (user) {
                    this.$store.dispatch('fetchTeam', user.team)
                }
                return user
            }
        },
        watch: {
            user: function() {
                this.update()
            }
        },
        methods: {
            updateSelectedCases: function(selections) {
                this.selected_cases = selections
            },
            displayID: function(d) {
                let to = `#/case/${ d.id }/`
                return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
            },
            displayCPRName: function(id) {
                return `${ id.cpr_number }<br>${ id.name }`
            },
            displayTargetGroupDistrict: function(id) {
                let str = `${ targetGroupId2name(id.target_group) }`
                if (id.target_group === 1) { 
                    str += `<dt>Skoledistrikt</dt><dd>${ districtId2name(id.district) }</dd></dl>`
                }
                return str
            },
            displayEffortName: function(id) {
                return displayEffort(id.effort_step)
            },
            displayUserTeam: function(id) {
                return `${ userId2name(id.case_worker) }<dl><dt>Team</dt><dd>${ teamId2name(id.team).name }</dd></dl>`
            },
            displayDate: function(d) {
                return json2js(d.modified)
            },
            displayStatus: function(d) {
                if (!d.expired) {
                    return `<div class="mini-label"><span class="label label-GRANTED">Aktiv</span></div>`
                }
                if (d.expired) {
                    return `<div class="mini-label"><span class="label label-CLOSED">Lukket</span></div>`
                }
            },
            displayAppr: function(id) {
                return `<dl class="appropriation-status"><dt>Foreløbige</dt><dd>${ id.num_draft_or_expected_appropriations }</dd><dt>I alt</dt><dd>${ id.num_appropriations }</dd></dl>`
            },
            diagChangeWorker: function(worker_id) {
                this.diag_field_case_worker = worker_id
            },
            moveCases: function() {
                let pks = []
                this.selected_cases.forEach(function(cas) {
                    pks.push(cas.id)
                })
                axios.patch('/cases/change_case_worker/', {
                    case_pks: pks,
                    case_worker_pk: this.diag_field_case_worker

                })
                .then(res => {
                    notify(`${ pks.length } sager blev flyttet`, 'success')
                    this.postDiagCleanUp()
                })
                .catch(err => {
                    notify('Noget gik galt under flytning af sager', 'error')
                    this.postDiagCleanUp()
                })
            },
            closeMoveDiag: function() {
                this.postDiagCleanUp()
            },
            postDiagCleanUp: function() {
                this.$refs['data-grid'].selection = []
                this.selected_cases = []
                let checkboxes = document.querySelectorAll('.datagrid-single-checkbox')
                checkboxes.forEach(function(node) {
                    node.checked = false
                })
                document.getElementById('datagrid-select-all').checked = false
                this.show_modal = false
                this.update()
            }
            
        },
        mounted: function() {
            this.update()
        }
    }
    
</script>

<style>

    .case-search {
        padding: 0 2rem 2rem;
    }

    .case-search-list {
        margin-top: 2rem;
        order: 2;
        flex-grow: 1;
    }

    .case-search .create {
        float: left;
        margin: -2rem 0 0 5rem;
    }

    .case-search-list .more .material-icons {
        margin: 0;
    }

    .case-search-filters {
        background-color: var(--grey1);
        padding: 0 1.5rem 1rem;
        margin-bottom: 3rem;
    }

    .case-search-filters--title {
        font-size: 1.125rem;
        padding: 1.5rem 0 .5rem;
    }

    .case-search-filters > form {
        padding: 0;
    }

    .case-search-filters .filter-fields {
        margin: 0;
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        align-items: flex-start;
    }

    .case-search-filters .filter-fields li {
        list-style: none;
        padding: .5rem 1rem .5rem 0;
    }

    .case-search-filters .filter-fields label {
        margin: 0;
    }

    .case-search-move-btn {
        height: auto;
        display: flex;
        align-items: center;
        padding: .125rem .66rem;
    }

    .move-cases-field label {
        margin-top: 0;
    }

    .datagrid-td-status {
        width: 8rem;
    }

    .case-search .appropriation-status {
        display: grid;
        grid-template-columns: auto auto;
    }

    .case-search .appropriation-status dt {
        padding-top: 0;
    }

    .case-search .appropriation-status dd {

    }

</style>
