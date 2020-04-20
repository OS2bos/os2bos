<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="appropriations">

        <data-grid ref="data-grid"
                   :data-list="apprs"
                   :columns="columns"
                   :selectable="false">
            
            <div slot="datagrid-header" class="appropriations-header">
                <h2 style="padding: 0;">Bevillingsskrivelser</h2>
                <button v-if="permissionCheck === true" class="appropriation-create-btn" @click="$router.push(`/case/${ caseId }/appropriation-create/`)">+ Opret bevillingsskrivelse</button>
            </div>

            <tr slot="datagrid-table-footer" class="summary">
                <td colspan="5"></td>
                <td class="right">Samlet</td>
                <td class="right nowrap"><strong>{{ displayDigits(total_granted) }} kr</strong></td>
                <td class="expected right nowrap">
                    <span v-if="has_expected">
                        {{ displayDigits(total_expected) }} kr.
                    </span>
                </td>
            </tr>

            <p slot="datagrid-footer" v-if="apprs.length < 1">
                Der er endnu ingen bevillingsskrivelser
            </p>

        </data-grid>

    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { sectionId2name, displayStatus } from '../filters/Labels.js'
    import UserRights from '../mixins/UserRights.js'
    import DataGrid from '../datagrid/DataGrid.vue'

    export default {

        mixins: [UserRights],
        components: {
            DataGrid
        },
        props: [
            'caseId'
        ],
        data: function() {
            return {
                apprs: [],
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
                        key: 'section',
                        title: 'Bevillingsparagraf',
                        display_func: this.displaySection,
                        class: 'nowrap'
                    },
                    {
                        key: 'note',
                        title: 'Supplerende info',
                        class: 'nowrap'
                    },
                    {
                        key: 'created',
                        title: 'Oprettet',
                        display_func: this.displayCreatedDate,
                        class: 'nowrap'
                    },
                    {
                        key: 'modified',
                        title: 'Senest ændret',
                        display_func: this.displayModifiedDate,
                        class: 'nowrap'
                    },
                    {
                        key: 'total_cost_full_year',
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
            total_granted: function() {
                function getTotal(total, a) {
                    return total + a.total_granted_this_year
                }
                if (this.apprs) {
                    return this.apprs.reduce(getTotal, 0)
                } else {
                    return false
                }
            },
            has_expected: function() {
                if (this.total_expected > 0 && this.total_expected !== this.total_granted) {
                    return true
                } else {
                    return false
                }
            },
            total_expected: function() {
                function getTotal(total, a) {
                    return total + a.total_expected_this_year
                }
                if (this.apprs) {
                    return this.apprs.reduce(getTotal, 0)
                } else {
                    return false
                }
            }
        },
        watch: {
            caseId: function() {
                this.fetchAppropriations()
            }
        },
        methods: {
            fetchAppropriations: function() {
                axios.get(`/appropriations/?case=${ this.caseId }`)
                .then(res => {
                    this.apprs = res.data
                })
                .catch(err => console.log(err))
            },
            displayCreatedDate: function(appr) {
                return json2jsDate(appr.created)
            },
            displayModifiedDate: function(appr) {
                return json2jsDate(appr.modified)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            displayGranted: function(appr) {
                for (let act in appr.activities) {
                    if (appr.total_granted_this_year) {
                        return `${ cost2da(appr.activities[act].total_cost_full_year) } kr.`
                    }
                }
            },
            displayExpected: function(appr) {
                if (appr.total_expected_this_year > 0 && appr.total_expected_this_year !== appr.total_granted_this_year) {
                    return `${ cost2da(appr.total_expected_full_year) } kr.`
                }
            },
            displaySection: function(appr) {
                return `§ ${ sectionId2name(appr.section) }`
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
                return `<a href="${ to }"><i class="material-icons">folder_open</i> ${ d.sbsys_id }</a>`
            }
        },
        created: function() {
            this.fetchAppropriations()
        }
    }
    
</script>

<style>

    .appropriations {
        margin: 0 0 2rem;
    }

    .appropriations-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .appropriation-create-btn {
        margin: 0 1rem;
    }

    .appropriations .status {
        font-weight: bold;
        color: black;
    }

    .appropriations tr.summary td {
        background-color: var(--grey0);
        padding-top: 1.5rem;
    }

    .datagrid-td-status {
        width: 8rem;
    }

    th.datagrid-td-status {
        padding-left: 1rem;
    }

</style>
