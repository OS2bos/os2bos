<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="case-search-list">
            
        <data-grid v-if="cases"
                ref="data-grid"
                :data-list="cases"
                :columns="columns"
                @selection="updateSelectedCases"
                :selectable="user_can_edit">
            <p slot="datagrid-footer" v-if="cases.length < 1">
                Kan ikke finde nogen resultater, der matcher de valgte kriterier
            </p>
        </data-grid>

        <button v-if="cases.length > 0 && user_can_edit"
                :disabled="selected_cases.length < 1" 
                class="case-search-move-btn"
                @click="show_modal = true">
            <i class="material-icons">forward</i>
            Flyt sager
        </button>            

        <dialog-box v-if="show_modal" @closedialog="closeMoveDiag">
            <h2 slot="header" style="padding: 0;">Flyt sager til en medarbejder</h2>
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
                <button type="submit" @click="moveCases">Flyt</button>
                <button type="button" @click="closeMoveDiag">Annuller</button>
            </div>
        </dialog-box>

    </div>
</template>

<script>
import axios from '../http/Http.js'
import DataGrid from '../datagrid/DataGrid.vue'
import DialogBox from '../dialog/Dialog.vue'
import notify from '../notifications/Notify.js'
import PermissionLogic from '../mixins/PermissionLogic.js'
import { json2js } from '../filters/Date.js'
import { targetGroupId2name, districtId2name, displayEffort, userId2name, teamId2name } from '../filters/Labels.js'

export default {
    components: {
        DataGrid,
        DialogBox
    },
    mixins: [
        PermissionLogic
    ],
    data: function() {
        return {
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
                    class: 'datagrid-action nowrap'
                },
                {
                    key: 'cpr_number',
                    title: 'CPR'
                },
                {
                    key: 'name',
                    title: 'Navn'
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
                    key: 'num_ongoing_appropriations',
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
        search_filters: function() {
            return this.$store.getters.getCaseSearchFilters
        },
        users: function() {
            return this.$store.getters.getUsers
        }
    },
    methods: {
        closeMoveDiag: function() {
            this.postDiagCleanUp()
        },
        diagChangeWorker: function(worker_id) {
            this.diag_field_case_worker = worker_id
        },
        displayAppr: function(id) {
            return `<dl class="appropriation-status"><dt>Foreløbige</dt><dd>${ id.num_ongoing_draft_or_expected_appropriations }</dd><dt>Aktive i alt</dt><dd>${ id.num_ongoing_appropriations }</dd></dl>`
        },
        displayEffortName: function(id) {
            return displayEffort(id.effort_step)
        },
        displayDate: function(d) {
            return json2js(d.modified)
        },
        displayID: function(d) {
            let to = `#/case/${ d.id }/`
            return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
        },
        displayStatus: function(d) {
            if (!d.expired) {
                return `<div class="mini-label"><span class="label label-GRANTED">Aktiv</span></div>`
            }
            if (d.expired) {
                return `<div class="mini-label"><span class="label label-CLOSED">Lukket</span></div>`
            }
        },
        displayTargetGroupDistrict: function(id) {
            let str = `${ targetGroupId2name(id.target_group) }`
            if (id.target_group === 1) { 
                str += `<dl><dt>Skoledistrikt</dt><dd>${ districtId2name(id.district) }</dd></dl>`
            }
            return str
        },
        displayUserTeam: function(id) {
            return `${ userId2name(id.case_worker) }<dl><dt>Team</dt><dd>${ teamId2name(id.team).name }</dd></dl>`
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
        postDiagCleanUp: function() {
            this.$refs['data-grid'].selection = []
            this.selected_cases = []
            let checkboxes = document.querySelectorAll('.datagrid-single-checkbox')
            checkboxes.forEach(function(node) {
                node.checked = false
            })
            document.getElementById('datagrid-select-all').checked = false
            this.show_modal = false
        },
        updateSelectedCases: function(selections) {
            this.selected_cases = selections
        }
    }
}
</script>

<style>

.case-search-list {
    margin-top: 1rem;
    order: 2;
    flex-grow: 1;
}

.case-search-list .more .material-icons {
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

</style>