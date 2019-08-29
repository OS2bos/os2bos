<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="activities">
        <button class="activities-create-btn" title="Ny aktivitet" @click="$router.push(`/appropriation/${ apprId }/activity-create/`)">+ Tilføj ydelse</button>
        <table v-if="acts && acts.length > 0">
            <thead>
                <tr>
                    <th style="width: 4.5rem;">
                        <input type="checkbox" id="check-all">
                        <label for="check-all"></label>
                    </th>
                    <th style="width: 5.5rem;">Status</th>
                    <th>Ydelse</th>
                    <th>Udbetales til</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th class="right">Udgift i år</th>
                    <th class="right">Forventet udgift i år</th>
                </tr>
                <tr>
                    <th colspan="7" class="table-heading">Ydelser</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in acts" :key="a.id" :class="{ 'expected-row': a.status === 'EXPECTED', 'adjustment-row': a.modifies }" :title="a.note">
                    <td style="width: 4.5rem;">
                        <input type="checkbox" :id="`check-${ a.id }`">
                        <label :for="`check-${ a.id }`"></label>
                    </td>
                    <td style="width: 5.5rem;">
                        <div class="mini-label" v-html="statusLabel(a.status)"></div>
                    </td>
                    <td>
                        <router-link :to="`/activity/${ a.id }`">{{ activityId2name(a.details) }}</router-link>
                        <span v-if="a.activity_type === 'MAIN_ACTIVITY'" class="act-label"><br>Hovedydelse</span>
                    </td>
                    <td>
                        {{ a.payment_plan.recipient_name }}
                        <span v-if="a.payment_plan.recipient_type === 'COMPANY'">
                            CVR
                        </span>
                        {{ a.payment_plan.recipient_id }}
                    </td>
                    <td class="nowrap">{{ displayDate(a.start_date) }}</td>
                    <td class="nowrap">{{ displayDate(a.end_date) }}</td>
                    <td class="nowrap right">
                        <span v-if="a.status === 'GRANTED'">{{ displayDigits(a.total_cost_this_year) }} kr</span>
                        <span v-if="a.status === 'DRAFT'" class="dim">{{ displayDigits(a.total_cost_this_year) }} kr</span>
                    </td>
                    <td class="nowrap right">
                        <span v-if="a.status === 'EXPECTED'" class="expected">{{ displayDigits(a.total_cost_this_year) }} kr</span>
                    </td>
                    
                </tr>
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
        <p v-if="!acts || acts.length < 1">Der er endnu ingen ydelser</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, displayStatus } from '../filters/Labels.js'

    export default {

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
            acts: function() {
                return this.$store.getters.getActivities
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
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            activityId2name: function(id) {
                return activityId2name(id)
            },
            statusLabel: function(status) {
                return displayStatus(status)
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
