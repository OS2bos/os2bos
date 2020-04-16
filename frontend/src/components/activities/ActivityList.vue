<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="activities">
        <header style="display: flex; flex-flow: row nowrap; align-items: center; margin: 2rem 0;">
            <h2 style="padding: 0;">Bevilgede ydelser</h2>
            <button v-if="permissionCheck === true" class="activities-create-btn" title="Ny aktivitet" @click="$router.push(`/appropriation/${ apprId }/activity-create/`)" style="margin: 0 1rem;">
                + Tilføj ydelse
            </button>
        </header>
        <table v-if="!no_acts">
            <thead>
                <tr>
                    <th style="width: 3.5rem; padding: .5rem 0 0 1.25rem;">
                        <input v-if="permissionCheck === true && this.user.profile !== 'edit'" type="checkbox" id="check-all" @change="setAllChecked" v-model="check_all_approvable">
                        <label class="disabled" for="check-all" title="Vælg alle"></label>
                    </th>
                    <th style="width: 6rem;">Status</th>
                    <th>Ydelse</th>
                    <th>Udbetales til</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th>Senest ændret</th>
                    <th class="right">Udgift i år</th>
                    <th class="right">Forventet udgift i år</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th></th>
                    <th colspan="7" class="table-heading" style="padding-top: .5rem;">Hovedydelse</th>
                </tr>
                <template v-for="chunk in main_acts">
                    <act-list-item 
                        v-for="a in chunk"
                        :ref="a.group ? a.group : a.id"
                        :act="a"
                        :key="a.id"
                        :checked="a.checked"
                        @toggle="toggleHandler"
                        @check="checkOneInList(a, ...arguments)" />
                </template>
                <tr v-if="suppl_acts.length > 0">
                    <th></th>
                    <th colspan="7" class="table-heading">Følgeydelser</th>
                </tr>
                <template v-for="chunk in suppl_acts">
                    <act-list-item 
                        v-for="a in chunk"
                        :ref="a.group ? a.group : a.id"
                        :act="a" 
                        :key="a.id"
                        :checked="a.checked"
                        @toggle="toggleHandler"
                        @check="checkOneInList(a, ...arguments)" />
                </template>
                <tr class="lastrow">
                    <td colspan="6" style="padding-left: 0;">
                        <button v-if="permissionCheck === true && this.user.profile !== 'edit'" @click="initPreApprove()" :disabled="approvable_acts.length < 1">✔ Godkend valgte</button>
                    </td>
                    <td class="right"><strong>I alt</strong></td>
                    <td class="nowrap right">
                        <strong>{{ displayDigits(appropriation.total_granted_this_year) }} kr.</strong>
                    </td>
                    <td class="nowrap expected right">
                        <span v-if="appropriation.total_expected_this_year !== appropriation.total_granted_this_year">
                            {{ displayDigits(appropriation.total_expected_this_year) }} kr.
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-if="no_acts">Der er endnu ingen ydelser</p>

        <approval-diag 
            v-if="diag_open" 
            :appr-id="apprId" 
            :acts="approvable_acts"
            :warning="diag_approval_warning"
            @close="closeDialog()" />

    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { cost2da } from '../filters/Numbers.js'
    import { displayStatus } from '../filters/Labels.js'
    import { json2jsEpoch } from '../filters/Date.js'
    import ActListItem from './ActivityListItem.vue'
    import ApprovalDiag from './Approval.vue'
    import UserRights from '../mixins/UserRights.js'

    export default {

        mixins: [UserRights],

        components: {
            ActListItem,
            ApprovalDiag
        },
        props: [
            'apprId'
        ],
        data: function() {
            return {
                chunks: [],
                main_acts: [],
                suppl_acts: [],
                check_all_approvable: false,
                approvable_acts: [],
                diag_open: false,
                diag_approval_warning: null
            }
        },
        computed: {
            appropriation: function() {
                return this.$store.getters.getAppropriation
            },
            acts: function() {
                return this.$store.getters.getActivities
            },
            no_acts: function() {
                if (this.acts.length < 1) {
                    return true
                } else {
                    return false
                }
            }
        },
        watch: {
            apprId: function() {
                this.update()
            },
            acts: function() {
                this.chunks = []
                this.splitActList(this.acts)
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchActivities', this.apprId)
            },
            closeDialog: function() {
                this.diag_open = false
                const checkboxes = document.querySelectorAll('input[type="checkbox"]')
                checkboxes.forEach(checkbox => {
                    checkbox.checked = false
                })
                this.approvable_acts = []
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            addModifierAct(chunk, id, act_list) {
                let modifiers = act_list.filter(function(a) {
                    return a.modifies === id
                })
                if (modifiers.length > 0) {
                    for (let m in modifiers) {
                        chunk.push(modifiers[m])
                        this.addModifierAct(chunk, modifiers[m].id, act_list)
                    }
                } else {
                    return chunk
                }
            },
            getBestDate(arr, criteria) {
                let best_date = null
                if (criteria === 'start') {
                    best_date = arr[0].start_date
                } else {
                    best_date = arr[arr.length - 1].end_date
                }
                return best_date
            },
            getBestModified(arr) {
                return arr[arr.length - 1].modified
            },
            checkExpected(arr) {
                return arr.find(function(a) {
                    return a.status === 'EXPECTED'
                }) ? 'EXPECTED' : arr[0].status
            },
            calcCost(arr) {
                let costs = {
                    approved: 0,
                    expected: 0
                }
                for (let a of arr) {
                    if (a.total_granted_this_year) {
                        costs.approved = costs.approved + a.total_granted_this_year
                    }
                    if (a.total_expected_this_year) {
                        costs.expected = costs.expected + a.total_expected_this_year
                    }
                }
                return costs
            },
            splitActList: function(act_list) {

                // Group activities together by 'modifies'
                for (let act of act_list) {
                    act.checked = false
                    if (act.modifies === null) {
                        let chunk = [act]
                        this.addModifierAct(chunk, act.id, act_list)
                        this.chunks.push(chunk)
                    }
                }
                
                // Add meta activity to chunks of modified activities
                for (let c in this.chunks) {
                    let chunk = this.chunks[c]
                    const clength = chunk.length,
                          last_chunk = chunk[clength -1]

                    if (clength < 2) {
                        // Do nothing
                    } else {
                        for (let act of chunk) {
                            act.group = `group${ c }`
                        }
                        let costs = this.calcCost(chunk),
                            meta_act = {
                                id: `group${ c }`,
                                is_meta: true,
                                status: this.checkExpected(chunk),
                                start_date: this.getBestDate(chunk,'start'),
                                end_date: this.getBestDate(chunk,'end'),
                                modified: this.getBestModified(chunk),
                                activity_type: last_chunk.activity_type,
                                approved: costs.approved,
                                expected: costs.expected,
                                details: last_chunk.details,
                                payment_plan: last_chunk.payment_plan,
                                note: last_chunk.note
                            }
                        chunk.unshift(meta_act)
                    }
                }

                // Populate main and supplementary activities lists
                this.main_acts = this.chunks.filter(function(c) {
                    return c[0].activity_type === 'MAIN_ACTIVITY'
                })
                let unsorted_suppl_acts = this.chunks.filter(function(c) {
                    return c[0].activity_type === 'SUPPL_ACTIVITY'
                })

                // Sort supplementary list by start date
                unsorted_suppl_acts.sort(function(a,b) {
                    const a_start_date = new Date(a[0].start_date).getTime(),
                          b_start_date = new Date(b[0].start_date).getTime()
                    if (a_start_date > b_start_date) {
                        return 1
                    } else if (b_start_date > a_start_date) {
                        return -1
                    } else {
                        return 0
                    }
                })
                this.suppl_acts = unsorted_suppl_acts
            },
            toggleHandler: function(toggl_id) {     
                for (let comp of this.$refs[toggl_id]) {
                    if (comp.act.is_meta) {
                        comp.toggled = !comp.toggled
                    } else {
                        comp.visible = !comp.visible
                    }       
                }
            },
            checkAllInList: function(check_val, list) {
                for (let arr of list) {
                    for (let a of arr) {
                        a.checked = check_val
                        if (a.checked && a.status !== 'GRANTED' && !a.is_meta) {
                            this.approvable_acts.push(a)
                        }
                    }
                }
            },
            checkOneInList: function(act, check_val) {
                const pre_checked_act = this.approvable_acts.findIndex(function(a) {
                    return a.id === act.id
                })
                if (check_val) {
                    if (pre_checked_act < 0) {
                        this.approvable_acts.push(act)
                    }
                } else {
                    if (pre_checked_act >= 0) {
                        this.approvable_acts.splice(pre_checked_act, 1)
                    }
                }
            },
            setAllChecked: function(event) {
                this.approvable_acts = []
                this.checkAllInList(event.target.checked, this.main_acts)
                this.checkAllInList(event.target.checked, this.suppl_acts)
            },
            initPreApprove: function() {

                // Logic to warn users about to shorten main activity running time
                // ... and thereby automatically shorten supplementary activities too
                this.diag_approval_warning = null
                const approvable_main_act = this.approvable_acts.find(function(act) {
                    return act.status === 'EXPECTED' && act.activity_type === 'MAIN_ACTIVITY'
                })
                if (approvable_main_act) {
                    const approvable_modifies = this.main_acts[0].find(activity => {
                        return activity.id === approvable_main_act.modifies
                    })
                    if (approvable_modifies && json2jsEpoch(approvable_main_act.end_date) < json2jsEpoch(approvable_modifies.end_date)) {
                        this.diag_approval_warning = 'Hvis du godkender, at hovedydelsen får kortere løbetid, kan det også ændre løbetiden for følgeydelserne.'
                    }
                }
                
                this.diag_open = true
            }
        },
        beforeCreate: function() {
            this.$store.commit('clearActivities')
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

    .activities {
        margin: 1rem;
    }

    .activities-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: flex-start;
        align-items: center;
    }

    .activities-create-btn {
        margin: 0 0 1rem;
    }

    .activities .act-label {
        opacity: .66;
        font-size: .85rem;
        margin: 0 1rem;
    }

    .activities input[type="checkbox"] + label {
        margin: 0;
    }

    .activities tr.lastrow td {
        background-color: var(--grey0);
        padding-top: 1.5rem;
    }

    .activities .table-heading {
        padding-left: .75rem;
    }

</style>
