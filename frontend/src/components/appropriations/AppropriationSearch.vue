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
            <h2 class="appropriation-search-filters--title">Filtre</h2>
            <form @submit.prevent>
                <fieldset>

                    <label for="field-sbsysid">SBSYS ID</label>
                    <input type="search" @input="update()" id="field-sbsysid" v-model="$route.query.case__sbsys_id">

                    <label for="field-cpr">Hovedsag CPR</label>
                    <input type="search" @input="changeCpr" id="field-cpr" v-model="$route.query.cpr_number">

                    <label for="field-team">Team</label>
                    <list-picker 
                        v-if="teams"
                        :dom-id="'field-team'" 
                        :selected-id="query.team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name"
                    />
                
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        v-if="users"
                        :dom-id="'field-case-worker'" 
                        :selected-id="query.case__case_worker"
                        :list="users"
                        @selection="changeWorker"
                        display-key="fullname"
                    />

                    <label for="field-section">Bevilling efter §</label>
                    <list-picker
                        v-if="sections"
                        class="resize"
                        :dom-id="'field-section'" 
                        :selected-id="query.section"
                        :list="sections"
                        @selection="changeSection"
                        display-key="paragraph"
                        display-key2="text"
                    />

                    <label for="field-main-act">Hovedydelse</label>
                    <list-picker 
                        v-if="appr_main_acts"
                        class="resize"
                        :dom-id="'field-main-act'" 
                        :selected-id="query.main_activity__details__id"
                        :list="appr_main_acts"
                        @selection="changeMainAct"
                        display-key="name"
                    />

                </fieldset>
            </form>
        </div>

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import { displayStatus, sectionId2name, activityId2name } from '../filters/Labels.js'
    import { cost2da } from '../filters/Numbers.js'
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
                act_details: [],
                selected_apprs: [],
                columns: [
                    {
                        key: 'status',
                        title: 'Status',
                        display_func: this.statusLabel,
                        class: 'mini-label datagrid-td-status'
                    },
                    {
                        key: 'sbsys_id',
                        title: 'Foranstaltningssag',
                        display_func: this.displayID,
                        class: 'datagrid-action nowrap'
                    },
                    {
                        key: 'case__sbsys_id',
                        title: 'SBSYS ID'
                    },
                    {
                        key: 'section',
                        title: 'Bevillingsparagraf',
                        display_func: this.displaySection,
                        class: 'nowrap'
                    },
                    {
                        key: 'case__cpr_number',
                        display_func: this.displayCPRName,
                        title: 'CPR nr.',
                    },
                    {
                        key: 'total_granted_full_year',
                        title: 'Udgift pr år',
                        display_func: this.displayGranted,
                        class: 'right nowrap'
                    },
                    {
                        key: 'total_expected_full_year',
                        title: 'Forventet udgift pr år',
                        display_func: this.displayExpected,
                        class: 'expected right nowrap'
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
            sections: function() {
                return this.$store.getters.getSections
            },
            appr_main_acts: function() {
                let actList = this.$store.getters.getActivityDetails.filter(act => act.main_activity_for.length > 0)
                return actList
            },
            user: function() {
                let user = this.$store.getters.getUser
                if (user) {
                    this.$store.dispatch('fetchTeam', user.team)
                }
                return user
            }
        },
        methods: {
            updateSelectedApprs: function(selections) {
                this.selected_apprs = selections
            },
            statusLabel: function(appr) {
                let label = 'DRAFT'
                for (let act in appr.activities) {
                    if (appr.activities[act].status === 'GRANTED') {
                        label = 'GRANTED'
                    }
                }
                for (let act in appr.activities) {
                    if (appr.activities[act].status === 'EXPECTED') {
                        label = 'EXPECTED'
                    }
                }
                return displayStatus(label)
            },
            displayID: function(d) {
                let to = `#/appropriation/${ d.id }/`
                return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
            },
            displayCPRName: function(d) {
                return `${ d.case__cpr_number } <br> ${ d.case__name }`
            },
            displaySection: function(d) {
                return `§ ${ sectionId2name(d.section) }`
            },
            displayActName: function(id) {
                return activityId2name(id)
            },
            displayGranted: function(appr) {
                return `${ cost2da(appr.total_granted_full_year) } kr.`
            },
            displayExpected: function(appr) {
                if (appr.total_expected_this_year > 0 && appr.total_expected_this_year !== appr.total_granted_this_year) {
                    return `${ cost2da(appr.total_expected_full_year) } kr.`
                }
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

    .appropriation-search-filters .resize {
        max-width: 18.5rem;
    }

    .appropriation-search-filters h2,
    .appropriation-search-filters form {
        padding: 0;
    }

    .datagrid-td-status {
        width: 8rem;
    }

</style>
