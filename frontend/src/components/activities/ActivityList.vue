<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="activities">
        <button class="activities-create-btn" title="Ny aktivitet" @click="$router.push(`/appropriation/${ apprId }/activity-create/`)">+ Tilføj ydelse</button>
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
        computed: {
            appropriation: function() {
                return this.$store.getters.getAppropriation
            },
            has_expected: function() {
                if (this.appropriation.total_expected_this_year > 0 && this.appropriation.total_granted_this_year !== this.appropriation.total_expected_this_year) {
                    return true
                } else {
                    return false
                }
            },
            main_acts: function() {
                return this.$store.getters.getMainActivities
            },
            suppl_acts: function() {
                return this.$store.getters.getSupplActivities
            },
            no_acts: function() {
                if (!this.main_acts && !this.suppl_acts) {
                    return true
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
            },
            displayDigits: function(num) {
                return cost2da(num)
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

    .activities tr:last-child td {
        background-color: var(--grey0);
        padding-top: 1.5rem;
    }

</style>
