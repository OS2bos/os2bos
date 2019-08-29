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
                <act-list-item v-for="a in main_acts" :data="a" :key="a.id" />
                <tr>
                    <th colspan="7" class="table-heading">Følgeydelser</th>
                    <th></th>
                </tr>
                <act-list-item v-for="a in suppl_acts" :data="a" :key="a.id" />
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
                suppl_acts: null,
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
                if (!this.main_acts && !this.suppl_acts) {
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

                function sortActsByModifier(list) {

                    let modifiers = list.filter(function(act) {
                            return act.modifies !== null
                        }),
                        modified = list.filter(function(act) {
                            return act.modifies === null
                        }),
                        new_list = Array.from(modified)

                    console.log('----')
                    console.log(modifiers)
                    
                    for (let m in modifiers) {
                        let idx = modified.findIndex(function(mod) {
                            return modifiers[m].modifies === mod.id
                        })
                        if (idx > -1) {
                            new_list.splice(idx, 0, modifiers[m])
                        }
                    }

                    console.log(modified)
                    console.log('----')

                    return new_list
                }

                function sortActsByDate(list) {
                    let new_list = list.sort(function(a,b) {
                        const a_start = new Date(a.start_date).getTime(),
                              b_start = new Date(b.start_date).getTime()
                        if (b_start > a_start) {
                            return -1
                        } else if (b_start < a_start) {
                            return 1
                        } else {
                            return 0
                        }
                    })
                    return new_list
                }

                let mains = sortActsByModifier( act_list.filter(function(act) { 
                        return act.activity_type === 'MAIN_ACTIVITY' 
                    }) ),
                    suppls = sortActsByModifier( act_list.filter(function(act) {
                        return act.activity_type === 'SUPPL_ACTIVITY'
                    }) )
                
                this.main_acts = mains
                this.suppl_acts = suppls
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
