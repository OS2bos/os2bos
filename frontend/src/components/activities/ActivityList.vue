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
            <button class="activities-create-btn" title="Ny aktivitet" @click="$router.push(`/appropriation/${ apprId }/activity-create/`)" style="margin: 0 1rem;">
                + Tilføj ydelse
            </button>
        </header>
        <table>
            <thead>
                <tr>
                    <th style="width: 4.5rem;">
                        <input type="checkbox" id="check-all" disabled>
                        <label class="disabled" for="check-all"></label>
                    </th>
                    <th style="width: 5.5rem;">Status</th>
                    <th>Ydelse</th>
                    <th>Udbetales til</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th class="right">Udgift i år</th>
                    <th class="right">Forventet udgift i år</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th colspan="7" class="table-heading" style="padding-top: 0;">Hovedydelse</th>
                    <th></th>
                </tr>
                <template v-for="chunk in main_acts">
                    <act-list-item 
                        v-for="a in chunk"
                        :ref="a.group ? a.group : a.id"
                        :act="a" 
                        :key="a.id"
                        @toggle="toggleHandler" />
                </template>
                <tr>
                    <th colspan="7" class="table-heading">Følgeydelser</th>
                    <th></th>
                </tr>
                <template v-for="chunk in suppl_acts">
                    <act-list-item 
                        v-for="a in chunk"
                        :ref="a.group ? a.group : a.id"
                        :act="a" 
                        :key="a.id"
                        @toggle="toggleHandler" />
                </template>
                <tr>
                    <td colspan="5" style="padding-left: 0;">
                        <button disabled>✔ Godkendt valgte</button>
                    </td>
                    <td class="right"><strong>I alt</strong></td>
                    <td class="nowrap right">
                        <strong>{{ displayDigits(appropriation.total_granted_this_year) }} kr</strong>
                    </td>
                    <td class="nowrap expected right">
                        {{ displayDigits(appropriation.total_expected_this_year) }} kr
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-if="no_acts">Der er endnu ingen ydelser</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { cost2da } from '../filters/Numbers.js'
    import { displayStatus } from '../filters/Labels.js'
    import ActListItem from './ActivityListItem.vue'

    export default {

        components: {
            ActListItem
        },
        props: [
            'apprId'
        ],
        data: function() {
            return {
                main_acts: null,
                suppl_acts: null
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
                this.splitActList(this.acts)
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchActivities', this.apprId)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            splitActList: function(act_list) {

                let chunks = []

                function addModifierAct(chunk, id) {
                    let modifier = act_list.find(function(a) {
                        return a.modifies === id
                    })
                    if (modifier) {
                        chunk.push(modifier)
                        addModifierAct(chunk, modifier.id)
                    } else {
                        chunks.push(chunk)
                    }   
                }

                // Group activities together by 'modifies'
                for (let act of act_list) {
                    if (act.modifies === null) {
                        let chunk = [act]
                        addModifierAct(chunk, act.id)
                    }
                }

                function getBestDate(arr, criteria) {
                    let best_date = null
                    for (let a in arr) {
                        const date = new Date( arr[a][`${ criteria}_date`] ).getTime()
                        if (criteria === 'start') {
                            if (!best_date || date < best_date) {
                                best_date = date
                            }
                        } else {
                            if (!best_date || date > best_date) {
                                best_date = date
                            }
                        }
                    }
                    return best_date
                }

                function checkExpected(arr) {
                    return arr.find(function(a) {
                        return a.status === 'EXPECTED'
                    }) ? 'EXPECTED' : arr[0].status
                }

                function calcCost(arr) {
                    let costs = {
                        draft: 0,
                        approved: 0,
                        expected: 0
                    }
                    for (let a of arr) {
                        if (a.status === 'GRANTED') {
                            costs.approved = costs.approved + a.total_cost_this_year
                        } else if (a.status === 'EXPECTED') {
                            costs.expected = costs.expected + a.total_cost_this_year
                        } else {
                            costs.draft = costs.draft + a.total_cost_this_year
                        }
                    }
                    costs.expected = costs.expected + costs.approved
                    return costs
                }

                // Add meta activity to chunks of modified activities
                for (let c in chunks) {
                    let chunk = chunks[c]
                    const clength = chunk.length,
                          last_chunk = chunk[clength -1]

                    if (clength < 2) {
                        // Do nothing
                    } else {
                        for (let act of chunk) {
                            act.group = `group${ c }`
                        }
                        let meta_act = {
                            id: `group${ c }`,
                            is_meta: true,
                            status: checkExpected(chunk),
                            start_date: getBestDate(chunk,'start'),
                            end_date: getBestDate(chunk,'end'),
                            activity_type: last_chunk.activity_type,
                            total_approved: calcCost(chunk).approved,
                            total_expected: calcCost(chunk).expected,
                            details: last_chunk.details,
                            payment_plan: last_chunk.payment_plan,
                            note: last_chunk.note
                        }
                        chunk.unshift(meta_act)
                    }
                }

                // Split list of chunks into main and supplementary lists
                this.main_acts = chunks.filter(function(c) {
                    return c[0].activity_type === 'MAIN_ACTIVITY'
                })
                this.suppl_acts = chunks.filter(function(c) {
                    return c[0].activity_type === 'SUPPL_ACTIVITY'
                })
                
            },
            toggleHandler: function(toggl_id) {     
                for (let comp of this.$refs[toggl_id]) {
                    if (comp.act.is_meta) {
                        comp.toggled = !comp.toggled
                    } else {
                        comp.visible = !comp.visible
                    }
                    
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

    .activities tr:last-child td {
        background-color: var(--grey0);
        padding-top: 1.5rem;
    }

</style>
