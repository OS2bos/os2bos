<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section class="activities">
        <header class="activities-header" style="margin-bottom: 0;">
            <div class="create-content">
                <h2 style="padding: 0;">
                    <i class="material-icons">style</i>
                    Bevilgede ydelser
                </h2>
                <button v-if="permissionCheck === true" class="btn activities-create-btn" title="Ny aktivitet" @click="createActivity">
                    + Tilføj ydelse
                </button>
            </div>
        </header>

        <fieldset class="act-list-actions" v-if="!no_acts">
            <div style="margin-left: 1.25rem;">
                <input 
                    v-if="permissionCheck === true && this.user.profile !== 'edit'" 
                    type="checkbox" 
                    id="check-all"
                    @change="setAllChecked">
                <label 
                    class="disabled" 
                    for="check-all">
                    Vælg alle
                </label>
            </div>
            <div>
                <label for="act-cost-toggle" style="margin: 0 .5rem 0 0; display: inline-block;">Vis udgifter</label>
                <select id="act-cost-toggle" class="selected-btn" v-model="selectedValue" style="margin: 0; display: inline-block;">
                    <option value="1">i år</option>
                    <option value="2">pr. år</option>
                    <option value="3">samlede</option>
                </select>
            </div>
        </fieldset>
        
        <div v-if="!no_acts" class="act-list-grid">

            <act-list :activities="main_activities" title="Hovedydelser" />
        
            <act-list :activities="suppl_activities" title="Følgeydelser" />

            <div class="act-list-row act-list-footer">
                <div style="grid-column: 1/8;">
                    <button 
                        v-if="permissionCheck === true && this.user.profile !== 'edit'" 
                        @click="initPreApprove"
                        :disabled="approvable_acts.length < 1">
                            ✔ Godkend valgte
                    </button>
                </div>
                <div class="right" style="grid-column: 8/9;">
                    <strong>I alt</strong>
                </div>
                <div class="nowrap right" style="grid-column: 9/10;">
                    <strong v-if="selectedValue <= '1'">{{ displayDigits(appropriation.total_granted_this_year) }} kr.</strong>
                    <strong v-if="selectedValue === '2'">{{ displayDigits(appropriation.total_granted_full_year) }} kr.</strong>
                    <strong v-if="selectedValue === '3'">{{ displayDigits(appropriation.total_cost_granted) }} kr.</strong>
                </div>
                <div class="nowrap expected right" style="grid-column: 10/11;">
                    <span v-if="appropriation.total_expected_this_year !== appropriation.total_granted_this_year && selectedValue <= '1'">
                        {{ displayDigits(appropriation.total_expected_this_year) }} kr.
                    </span>
                    <span v-if="appropriation.total_expected_this_year !== appropriation.total_granted_this_year && selectedValue === '2'">
                        {{ displayDigits(appropriation.total_expected_full_year) }} kr.
                    </span>
                    <span v-if="appropriation.total_expected_this_year !== appropriation.total_granted_this_year && selectedValue === '3'">
                        {{  displayDigits(appropriation.total_cost_expected) }} kr.
                    </span>
                </div>
            </div>
        
        </div>

        <p v-else>Der er endnu ingen ydelser</p>

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
    import ApprovalDiag from './Approval.vue'
    import UserRights from '../mixins/UserRights.js'
    import ActList from './activitylist/ActList.vue'

    export default {

        mixins: [
            UserRights
        ],
        components: {
            ApprovalDiag,
            ActList
        },
        props: [
            'apprId'
        ],
        data: function() {
            return {
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
            main_activities: function() {
                if (this.acts) {
                    return this.acts.filter(function(act) {
                        return act.activity_type === 'MAIN_ACTIVITY'
                    })
                }
            },
            suppl_activities: function() {
                if (this.acts) {
                    let unsorted_acts = this.acts.filter(function(act) {
                        return act.activity_type === 'SUPPL_ACTIVITY'
                    })
                    return this.sortSupplementaryActs(unsorted_acts)
                }
            },
            no_acts: function() {
                if (this.acts.length < 1) {
                    return true
                } else {
                    return false
                }
            },
            approvable_acts: function() {
                return this.$store.getters.getCheckedItems
            },
            selectedValue: {
                get: function() {
                    return this.$store.getters.getSelectedCostCalc
                },
                set: function(new_val) {
                    this.$store.commit('setSelectedCostCalc', new_val)
                    this.update()
                }
            }
        },
        watch: {
            apprId: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchActivities', this.apprId)
                this.$store.commit('setUnCheckAll')
            },
            closeDialog: function() {
                this.diag_open = false
                const checkboxes = document.querySelectorAll('input[type="checkbox"]')
                checkboxes.forEach(checkbox => {
                    checkbox.checked = false
                })
                this.$store.commit('setCheckedItems', [])
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            sortSupplementaryActs: function(acts) {
                // Sort supplementary list by start date
                return acts.sort(function(a,b) {
                    const a_start_date = new Date(a.start_date).getTime(),
                        b_start_date = new Date(b.start_date).getTime()
                    if (a_start_date > b_start_date) {
                        return 1
                    } else if (b_start_date > a_start_date) {
                        return -1
                    } else {
                        return 0
                    }
                })
            },
            checkAllInList: function(check_val, list) {
                for (let a in list) {
                    list[a].checked = check_val
                    if (list[a].checked && list[a].status !== 'GRANTED') {
                        this.$store.commit('setCheckedItem', list[a])
                    }
                }
            },
            setAllChecked: function(event) {
                this.$store.commit('setCheckedItems', [])
                this.checkAllInList(event.target.checked, this.main_activities)
                this.checkAllInList(event.target.checked, this.suppl_activities)
            },
            initPreApprove: function() {

                // Logic to warn users about to shorten main activity running time
                // ... and thereby automatically shorten supplementary activities too
                this.diag_approval_warning = null
                const approvable_main_act = this.approvable_acts.find(function(act) {
                    return act.status === 'EXPECTED' && act.activity_type === 'MAIN_ACTIVITY'
                })
                if (approvable_main_act) {
                    const approvable_modifies = this.main_activities.find(activity => {
                        return activity.id === approvable_main_act.modifies
                    })
                    if (approvable_modifies && json2jsEpoch(approvable_main_act.end_date) < json2jsEpoch(approvable_modifies.end_date)) {
                        this.diag_approval_warning = 'Hvis du godkender, at hovedydelsen får kortere løbetid, kan det også ændre løbetiden for følgeydelserne.'
                    }
                }
                this.diag_open = true
            },
            createActivity: function() {
                if (this.main_activities.length > 0) {
                    this.$router.push('/activity/create?type=supplementary')
                } else {
                    this.$router.push('/activity/create?type=main')
                }
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

    .act-list-row {
        display: grid;
        grid-template-columns: 3.5rem 6rem 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
        margin-bottom: .125rem;
        align-items: center;
    }

    .act-list-row {
        background-color: var(--grey1);
    }

    .act-list-row.act-list-footer {
        background-color: var(--grey0);
    }

    .act-list-row > div {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding: .5rem .5rem;
    }

    .act-list-actions {
        padding: 0; 
        margin: 1rem 0 0;
    }

    .act-list-actions > div {
        float: right;
        max-width: 50%;
    }

    .act-list-actions > div:first-child {
        float: left;
    }

    .act-list-footer {
        margin-top: 1.5rem;
    }

    .act-list-footer > div:first-child {
        padding-left: 0;
    }

    .activities .create-content {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .activities .activities-create-btn {
        margin: 0 1rem;
    }

</style>