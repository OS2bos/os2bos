<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="appropriations">
        <header class="appropriations-header">
            <h1>Bevillingsskrivelser</h1>
            <button class="appropriation-create-btn" @click="$router.push(`/case/${ caseId }/appropriation-create/`)">+ Opret bevillingsskrivelse</button>
        </header>
        <table class="appropriation-list" v-if="apprs && apprs.length > 0">
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Foranstaltningssag nr.</th>
                    <th>Bevillingsparagraf</th>
                    <th>Supplerende information</th>
                    <th>Oprettet</th>
                    <th>Senest ændret</th>
                    <th style="text-align: right">Bevilget i år</th>
                    <th style="text-align: right">Forventet i år</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in apprs" :key="a.id">
                    <td><div v-html="statusLabel(a.status)"></div></td>
                    <td>    
                        <i class="material-icons">folder_open</i>
                        <router-link :to="`/appropriation/${ a.id }`">
                            {{ a.sbsys_id }} 
                        </router-link>
                    </td>
                    <td>§ {{ displaySection(a.section) }}</td>
                    <td>{{ a.note }}</td>
                    <td>{{ displayDate(a.created) }}</td>
                    <td>{{ displayDate(a.modified) }}</td>
                    <td style="text-align: right">{{ displayDigits(a.total_granted_this_year) }} kr</td>
                    <template v-if="a.total_expected_this_year > 0 && a.total_expected_this_year !== a.total_granted_this_year">
                        <td class="expected" style="text-align: right">{{ displayDigits(a.total_expected_this_year) }} kr</td>
                    </template>
                    <td v-else></td>
                    
                </tr>
                <tr>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="text-align: right; border: none;">Samlet</td>
                    <td style="text-align: right; border: none;"><strong>{{ displayDigits(total_granted) }} kr</strong></td>
                    <template v-if="has_expected">
                        <td class="expected" style="text-align: right; border: none;">{{ displayDigits(total_expected) }} kr</td>
                    </template>
                    <td style="border: none;" v-else></td>
                </tr>
            </tbody>
        </table>
        <p v-if="!apprs || apprs.length < 1">Der er endnu ingen bevillingsskrivelser</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { sectionId2name, displayStatus } from '../filters/Labels.js'

    export default {

        props: [
            'caseId'
        ],
        data: function() {
            return {
                apprs: null   
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
            displayDate: function(dt) {
                return json2js(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            displaySection: function(id) {
                return sectionId2name(id)
            },
            statusLabel: function(status) {
                return displayStatus(status)
            }
        },
        created: function() {
            this.fetchAppropriations()
        }
    }
    
</script>

<style>

    .appropriations {
        margin: 2rem 0;
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

    .appropriations .expected {
        background-color: hsl(var(--color3), 80%, 80%); 
    }

</style>
