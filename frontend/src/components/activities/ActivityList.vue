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
                <button v-if="user_can_edit === true" class="btn activities-create-btn" title="Ny aktivitet" @click="createActivity">
                    + Tilføj ydelse
                </button>
            </div>
        </header>
        <fieldset class="act-list-actions" v-if="!no_acts">
            <div style="margin-left: 1.25rem;">
                <input 
                    v-if="user_can_edit === true && this.user.profile !== 'edit'" 
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
                    <option :value="previous_year">{{ previous_year }}</option>
                    <option :value="this_year">{{ this_year }}</option>
                    <option :value="next_year">{{ next_year }}</option>
                </select>
            </div>
        </fieldset>
        
        <div v-if="!no_acts" class="act-list-grid">

            <act-list :activities="main_activities" title="Hovedydelser" />
        
            <act-list :activities="suppl_activities" title="Følgeydelser" />

            <div class="act-list-row act-list-footer">
                <div style="grid-column: 1/8;">
                    <button 
                        v-if="user_can_edit === true && this.user.profile !== 'edit'" 
                        @click="initPreApprove"
                        :disabled="approvable_acts.length < 1">
                            ✔ Godkend valgte
                    </button>
                </div>
                <div class="right" style="grid-column: 8/9;">
                    <strong>I alt</strong>
                </div>
                <div class="nowrap right" style="grid-column: 9/10;">
                    <strong>{{ displayGrantedYearly() }}</strong>
                </div>
                <div class="nowrap expected right" style="grid-column: 10/11;">
                    {{ displayExpectedYearly() }}
                </div>
            </div>
        
        </div>

        <p v-else>Der er endnu ingen ydelser</p>

        <approval-diag 
            v-if="diag_open" 
            :appr-id="apprId" 
            :acts="approvable_acts"
            :warning="diag_approval_warning"
            @close="closeDialog" 
            @updated="update(apprId)" />

    </section>

</template>

<script>

    import { cost2da } from '../filters/Numbers.js'
    import { json2jsEpoch } from '../filters/Date.js'
    import ApprovalDiag from './Approval.vue'
    import PermissionLogic from '../mixins/PermissionLogic.js'
    import ActList from './activitylist/ActList.vue'

    export default {

        mixins: [
            PermissionLogic
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
                diag_approval_warning: null,
                this_year: String(new Date().getUTCFullYear()),
                next_year: String(new Date().getUTCFullYear() + 1),
                previous_year: String(new Date().getUTCFullYear() - 1),
            }
        },
        computed: {
            acts: function() {
                return this.$store.getters.getActivities
            },
            appropriation: function() {
                return this.$store.getters.getAppropriation
            },
            main_activities: function() {
                if (this.acts) {
                    return this.acts.filter(function(act) {
                        return act.activity_type === 'MAIN_ACTIVITY'
                    })
                } else {
                    return []
                }
            },
            suppl_activities: function() {
                if (this.acts) {
                    let unsorted_acts = this.acts.filter(function(act) {
                        return act.activity_type === 'SUPPL_ACTIVITY'
                    })
                    return this.sortSupplementaryActs(unsorted_acts)
                } else {
                    return []
                }
            },
            no_acts: function() {
                if (!this.acts || this.acts.length < 1) {
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
                    this.update(this.apprId)
                }
            }
        },
        methods: {
            update: function(appropriation_id) {
                this.fetchActListData(appropriation_id)
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
            displayGrantedYearly: function() {
                switch(this.selectedValue) {
                    case this.previous_year:
                        return this.displayDigits(this.appropriation.total_granted_previous_year) + ' kr.'
                    case this.next_year:
                        return this.displayDigits(this.appropriation.total_granted_next_year) + ' kr.'
                    default:
                        return this.displayDigits(this.appropriation.total_granted_this_year) + ' kr.'
                }
            },
            displayExpectedYearly: function() {
                switch(this.selectedValue) {
                    case this.previous_year:
                        return this.displayDigits(this.appropriation.total_expected_previous_year) + ' kr.'
                    case this.next_year:
                        return this.displayDigits(this.appropriation.total_expected_next_year) + ' kr.'
                    default:
                        return this.displayDigits(this.appropriation.total_expected_this_year) + ' kr.'
                }
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
            },
            fetchActListData: function(appropriation_id) {
                const id = btoa(`Appropriation:${appropriation_id}`)
                let data = {
                    query: `{
                        appropriation(id: "${ id }") {
                            activities {
                                edges {
                                    node {
                                        pk,
                                        status,
                                        note,
                                        activityType,
                                        startDate,
                                        endDate,
                                        modified,
                                        details {
                                            name,
                                            pk
                                        },
                                        modifies {
                                            pk
                                        },
                                        totalGrantedThisYear,
                                        totalExpectedThisYear,
                                        totalCostFullYear,
                                        totalCost,
                                        totalCostThisYear,
                                        paymentPlan {
                                            recipientId,
                                            recipientName,
                                            fictive,
                                            paymentMethod
                                        }
                                    }
                                }
                            }
                        }
                    }`
                }
                axios.post('/graphql/', data)
                .then(res => {
                    if (!res.data.data.appropriation) {
                        return false
                    }
                    const edges = res.data.data.appropriation.activities.edges 
                    const acts = edges.map(a => {
                        return {
                            id: a.node.pk,
                            status: a.node.status,
                            details: a.node.details.pk,
                            details_data: {
                                name: a.node.details.name
                            },
                            note: a.node.note,
                            start_date: a.node.startDate,
                            end_date: a.node.endDate,
                            modified: a.node.modified,
                            activity_type: a.node.activityType,
                            modifies: a.node.modifies ? a.node.modifies.pk : null,
                            total_granted_this_year: a.node.totalGrantedThisYear,
                            total_expected_this_year: a.node.totalExpectedThisYear,
                            total_cost_full_year: a.node.totalCostFullYear,
                            total_cost: a.node.totalCost,
                            approved: a.node.status === 'GRANTED' ? true : false,
                            expected: a.node.status === 'EXPECTED' ? true : false,
                            payment_plan: {
                                fictive: a.node.paymentPlan.fictive,
                                recipient_name: a.node.paymentPlan.recipientName,
                                recipient_id: a.node.paymentPlan.recipientId,
                                payment_method: a.node.paymentPlan.paymentMethod
                            }
                        }
                    })
                    this.$store.commit('setActivityList', acts)
                    const reducer = function(acc,val) {
                        const new_acc = {
                            node: {
                                totalGrantedThisYear: Number(acc.node.totalGrantedThisYear) + Number(val.node.totalGrantedThisYear),
                                totalExpectedThisYear: Number(acc.node.totalExpectedThisYear) + Number(val.node.totalExpectedThisYear),
                                totalCostFullYear: Number(acc.node.totalCostFullYear) + Number(val.node.totalCostFullYear),
                                totalCostThisYear: Number(acc.node.totalCostThisYear) + Number(val.node.totalCostThisYear),
                                totalCost: Number(acc.node.totalCost) + Number(val.node.totalCost)
                            }
                        }
                        return new_acc
                    }
                    if (edges.length > 0) {
                        const new_appropriation = edges.reduce(reducer)
                        // TODO: total_expected_full_year and total_cost_expected missing. Other mismatches in data?
                        this.total_costs = {
                            total_granted_this_year: new_appropriation.node.totalGrantedThisYear,
                            total_expected_this_year: new_appropriation.node.totalExpectedThisYear,
                            total_granted_full_year: new_appropriation.node.totalCostFullYear,
                            total_expected_full_year: 'ukendt',
                            total_cost_granted: new_appropriation.node.totalCost,
                            total_cost_expected: 'ukendt'
                        }
                    }
                })
            }
        },
        watch: {
            apprId: function(new_val) {
                this.update(new_val)
            }
        },
        created: function() {
            this.update(this.apprId)
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