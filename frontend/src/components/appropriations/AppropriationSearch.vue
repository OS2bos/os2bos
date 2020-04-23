<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="appropriation-search">
        
        <div class="appropriation-search-list">

            <data-grid
                       ref="data-grid"
                       :data-list="apprs"
                       :columns="columns"
                       @selection="updateSelectedApprs">

                <div slot="datagrid-header">
                    <h1 style="padding: 0;">Bevillinger</h1>
                </div>
                <p slot="datagrid-footer" v-if="apprs.length < 1">
                    Kan ikke finde nogen resultater, der matcher de valgte kriterier
                </p>

            </data-grid>

        </div>

        <div class="appropriation-search-filters">
            <h2>Filtre</h2>
            <form @submit.prevent>
                <fieldset>

                    <label for="field-sbsysid">SBSYS ID</label>
                    <input type="search" @input="update()" id="field-sbsysid" v-model="$route.query.sbsys_id">

                    <label for="field-cpr">Hovedsag CPR</label>
                    <input type="search" @input="changeCpr" id="field-cpr" v-model="$route.query.cpr_number">

                    <label for="field-team">Team</label>
                    <list-picker 
                        v-if="apprs"
                        :dom-id="'field-team'" 
                        :selected-id="query.team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name"
                    />
                
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        v-if="apprs"
                        :dom-id="'field-case-worker'" 
                        :selected-id="query.case_worker"
                        :list="users"
                        @selection="changeWorker"
                        display-key="fullname"
                    />

                    <label for="field-section">Bevilling efter §</label>
                    <list-picker 
                        v-if="apprs"
                        :dom-id="'field-section'" 
                        :selected-id="query.section"
                        :list="apprs"
                        @selection="changeSection"
                        display-key="section"
                    />

                    <label for="field-main-act">Hovedydelse</label>
                    <list-picker 
                        v-if="apprs"
                        :dom-id="'field-main-act'" 
                        :selected-id="query.main_activity"
                        :list="apprs"
                        @selection="changeMainAct"
                        display-key="main_activity"
                    />

                </fieldset>
            </form>
        </div>

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import { sectionId2name, activityId2name } from '../filters/Labels.js'
    import ListPicker from '../forms/ListPicker.vue'
    import AppropriationFilters from '../mixins/AppropriationFilters.js'

    export default {

        components: {
            DataGrid,
            ListPicker
        },
        mixins: [
            AppropriationFilters
        ],
        data: function() {
            return {
                selected_apprs: [],
                columns: [
                    {
                        key: 'case',
                        title: 'SBSYS ID',
                        display_func: this.displayCaseID,
                        class: 'datagrid-action'
                    },
                    {
                        key: 'sbsys_id',
                        title: 'Foranstaltningssag',
                        display_func: this.displayID,
                        class: 'datagrid-action'
                    },
                    {
                        key: 'section',
                        title: 'Bevillingsparagraf',
                        display_func: this.displaySection,
                        class: 'nowrap'
                    },
                    {
                        key: 'case__cpr_number',
                        title: 'CPR nr.',
                    }
                ]
            }
        },  
        computed: {
            cas: function() {
                return this.$store.getters.getCase
            },
            apprs: function() {
                return this.$store.getters.getAppropriations
            },
            users: function() {
                return this.$store.getters.getUsers
            },
            teams: function() {
                return this.$store.getters.getTeams
            },
            appr_main_acts: function() {
                return this.$store.getters.getAppropriationMainActs
            }
        },
        methods: {
            updateSelectedApprs: function(selections) {
                this.selected_apprs = selections
            },
            displayCaseID: function(d) {
                let to = `#/case/${ d.id }/`
                return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.case }</a>`
            },
            displayID: function(d) {
                let to = `#/appropriation/${ d.id }/`
                return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
            },
            displaySection: function(apprs) {
                return `§ ${ sectionId2name(apprs.section) }`
            },
            displayActName: function(id) {
                return activityId2name(id)
            }
        },
        mounted: function() {
            this.update()
        }
    }
    
</script>

<style>

    .appropriation-search {
        padding: 0 2rem 2rem;
        display: flex;
        flex-flow: row nowrap;
    }

    .appropriation-search-list {
        order: 2;
        flex-grow: 1;
    }

    .appropriation-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 1.5rem 1rem 0;
        margin: 1.25rem 1.25rem 0 0;
    }

    .appropriation-search-filters h2,
    .appropriation-search-filters form {
        padding: 0;
    }

    .datagrid-td-status {
        width: 8rem;
    }

</style>
