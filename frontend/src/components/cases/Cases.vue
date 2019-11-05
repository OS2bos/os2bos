<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="case-search">
        
        <div class="case-search-list">
            <h1 style="padding-top: 0;">Sager</h1>

            <div v-if="cases.length > 0">
                <data-grid :data-list="cases"
                           :columns="columns"
                           @selection="updateSelectedCases"
                           :selectable="true" />
                <button :disabled="selected_cases.length < 1" 
                        class="case-search-move-btn"
                        @click="openCaseMoveDiag()">
                    <i class="material-icons">forward</i>
                    Flyt sager
                </button>
            </div>

            <p v-if="cases.length < 1">
                Kan ikke finde nogen sager, der matcher de valgte kriterier
            </p>

        </div>

        <div class="case-search-filters">
            <h2>Filtre</h2>
            <form @submit.prevent>
                <fieldset>

                    <label for="field-cpr">CPR-nr</label>
                    <input type="search" @input="changeCpr()" id="field-cpr" v-model="field_cpr">

                    <label for="field-team">Team</label>
                    <list-picker 
                        :dom-id="'field-team'" 
                        :selected-id="field_team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name" />
                
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        :dom-id="'field-case-worker'" 
                        :selected-id="field_case_worker"
                        :list="users"
                        @selection="changeWorker"
                        display-key="fullname" />
                
                </fieldset>
                <fieldset>

                    <input type="checkbox" v-model="field_expired" id="field-expired" @change="changeExpired()">
                    <label for="field-expired">Kun udgåede sager</label>

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

    export default {

        components: {
            DataGrid,
            ListPicker
        },
        data: function() {
            return {
                selected_cases: [],
                field_cpr: null,
                field_case_worker: null,
                field_team: null,
                field_expired: false,
                columns: [
                    {
                        key: 'expired',
                        title: 'Status',
                        display_func: this.displayStatus
                    },
                    {
                        key: 'sbsys_id',
                        title: 'SBSYS ID',
                        display_func: this.displayID,
                        clickable: true
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
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchCases', this.$route.query)
            },
            updateSelectedCases: function(selections) {
                this.selected_cases = selections
            },
            displayID: function(d) {
                let to = `#/case/${ d.id }/`
                return `<a href="${ to }">${ d.sbsys_id }</a>`
            },
            displayDate: function(d) {
                return json2js(d.modified)
            },
            displayStatus: function(d) {
                if (!d.expired) {
                    return `
                        <div class="mini-label">
                            <span class="label label-GRANTED">Aktiv</span>
                        </div>
                    `
                }   
            },
            changeCpr: function() {
                let cpr = this.field_cpr.replace('-','')
                if (cpr.length === 10) {
                    this.$route.query.cpr_number = cpr
                    this.update()
                } else if (!cpr) {
                    this.$route.query.cpr_number = ''
                    this.update()
                }
            },
            changeWorker: function(worker_id) {
                this.$route.query.case_worker = worker_id
                this.update()
            },
            changeTeam: function(team_id) {
                this.$route.query.team = team_id
                this.update()
            },
            changeExpired: function() {
                this.$route.query.expired = this.field_expired
                this.update()
            },
            openCaseMoveDiag: function() {

            }
        },
        created: function() {
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
    }

    .case-search-list .more .material-icons {
        margin: 0;
    }

    .case-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 1rem;
        margin: 2.9rem 2rem 0 0;
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

</style>
