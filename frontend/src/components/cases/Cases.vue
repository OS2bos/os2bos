<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="case-search">
        
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

        <div class="case-search-filters">
            <h2>Filtre</h2>
            <form @submit.prevent>
                <fieldset>

                    <label for="field-sbsysid">SBSYS ID</label>
                    <input type="search" @input="update()" id="field-sbsysid" v-model="$route.query.sbsys_id">

                    <label for="field-cpr">CPR-nr</label>
                    <input type="search" @input="changeCpr" id="field-cpr" v-model="$route.query.cpr_number">

                    <label for="field-team">Team</label>
                    <list-picker 
                        v-if="teams"
                        :dom-id="'field-team'" 
                        :selected-id="query.team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name" />
                
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        v-if="users"
                        :dom-id="'field-case-worker'" 
                        :selected-id="query.case_worker"
                        :list="users"
                        @selection="changeWorker"
                        display-key="fullname" />
                
                </fieldset>
                <fieldset>

                    <input type="radio" v-model="$route.query.expired" id="field-expired-1" @change="update()" :value="null">
                    <label for="field-expired-1">Aktive og lukkede sager</label>
                    <input type="radio" v-model="$route.query.expired" id="field-expired-2" @change="update()" :preselected="selectedCases" :value="false">
                    <label for="field-expired-2">Kun aktive sager</label>
                    <input type="radio" v-model="$route.query.expired" id="field-expired-3" @change="update()" :value="true">
                    <label for="field-expired-3">Kun lukkede sager</label>

                </fieldset>
            </form>
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
                        title: 'CPR nr.',
                    },
                    {
                        key: 'name',
                        title: 'Navn',
                    },
                    {
                        title: 'Foreløbige',
                        display_func: this.actCountTotal
                    },
                    {
                        title: 'Bev.',
                        display_func: this.actCountTotal
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
            },
            selectedUser: function() {
                let user = this.$store.getters.getUser
                if (user) {
                    this.$store.dispatch('fetchTeam', user.team)
                }
                if (user.id) {
                    return this.query.case_worker = user.id
                }
            },
            selectedCases: function() {
                this.$route.query.expired = false
                this.update()
                return this.$route.query.expired
            }
        },
        watch: {
            selectedUser: function() {
                this.update()
            },
            user: function() {
                this.update()
            }
        },
        methods: {
            actCountTotal: function() {
                return `-`
            },
            updateSelectedCases: function(selections) {
                this.selected_cases = selections
            },
            displayID: function(d) {
                let to = `#/case/${ d.id }/`
                return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
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
        display: flex;
        flex-flow: row nowrap;
    }

    .case-search-list {
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
        order: 1;
        background-color: var(--grey1);
        padding: 1.5rem 1rem 0;
        margin: 1.25rem 1.25rem 0 0;
    }

    .case-search-filters h2,
    .case-search-filters form {
        padding: 0;
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

</style>
