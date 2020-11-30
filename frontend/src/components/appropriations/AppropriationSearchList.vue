<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="appropriation-search-list">

      <data-grid v-if="apprs"
              ref="data-grid"
              :data-list="apprs"
              :columns="columns"
              @selection="updateSelectedApprs">

          <p slot="datagrid-footer" v-if="apprs.length < 1">
              Kan ikke finde nogen resultater, der matcher de valgte kriterier
          </p>

      </data-grid>

    </div>
</template>

<script>
  import axios from '../http/Http.js'
  import DataGrid from '../datagrid/DataGrid.vue'
  import { displayStatus, sectionId2name, activityId2name } from '../filters/Labels.js'
  import { cost2da } from '../filters/Numbers.js'

  export default {

    components: {
        DataGrid
    },
    data: function() {
        return {
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
                    key: 'note',
                    title: 'Supplerende oplysninger',
                    display_func: this.displayNote,
                    class: 'nowrap'
                },
                {
                    key: 'main_activity__details__id',
                    title: 'Hovedydelse',
                    display_func: this.displayMainAct,
                    class: 'nowrap'
                },
                {
                    key: 'case__cpr_number',
                    title: 'CPR nr.',
                },
                {
                    key: 'case__name',
                    title: 'Navn',
                },
                {
                    key: 'num_ongoing_activities',
                    title: 'Ydelser',
                    display_func: this.displayActs,
                    class: 'nowrap'
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
        apprs: function() {
            return this.$store.getters.getAppropriations
        }
    },
    methods: {
        updateSelectedApprs: function(selections) {
            this.selected_apprs = selections
        },
        statusLabel: function(appr) {
            let label = 'DRAFT'
                if (appr.status === 'GRANTED') {
                    label = 'GRANTED'
                }
                if (appr.status === 'EXPECTED') {
                    label = 'EXPECTED'
                }
            return displayStatus(label)
        },
        displayID: function(d) {
            let to = `#/appropriation/${ d.id }/`
            return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
        },
        displaySection: function(d) {
            return `§ ${ sectionId2name(d.section) }`
        },
        displayNote: function(appr) {
            if (appr.note) {
                return `${ appr.note }`
            } else {
                return `-`
            }
        },
        displayMainAct: function(appr) {
            return `${ activityId2name(appr.main_activity__details__id) }`
        },
        displayGranted: function(appr) {
            return `${ cost2da(appr.total_granted_full_year) } kr.`
        },
        displayExpected: function(appr) {
            if (appr.total_expected_this_year > 0 && appr.total_expected_this_year !== appr.total_granted_this_year) {
                return `${ cost2da(appr.total_expected_full_year) } kr.`
            }
        },
        displayActs: function(id) {
            return `<dl class="num-acts"><dt>Foreløbige</dt><dd>${ id.num_ongoing_draft_or_expected_activities }</dd><dt>Aktive i alt</dt><dd>${ id.num_ongoing_activities }</dd></dl>`
        }
    }
  }
    
</script>

<style>

    .appropriation-search-list {
        margin-top: 1rem;
        order: 2;
        flex-grow: 1;
    }

    .datagrid-td-status {
        width: 8rem;
    }

    .appropriation-search-list .num-acts {
        display: grid;
        grid-template-columns: auto auto;
    }

    .appropriation-search-list .num-acts dt {
        padding-top: 0;
    }

</style>
