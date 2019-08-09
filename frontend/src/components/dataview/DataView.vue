<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="dataview">
        <table>
            <thead>
                <tr>
                    <th>Ydelse</th>
                    <th>Udgift i år</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in activities" :key="a.id">
                    <td>{{ displayActName(a.details) }}</td>
                    <td>{{ a.total_cost_this_year }} kr</td>
                </tr>
            </tbody>
        </table>
        
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { activityId2name } from '../filters/Labels.js'

    export default {

        data: function() {
            return {
                rows: null
            }
        },
        computed: {
            activities: function() {
                return this.$store.getters.getActivities
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchActivities')
            },
            displayActName: function(id) {
                return activityId2name(id)
            }
        },
        created: function() {
            this.update()
        }
        
    }
    
</script>

<style>

    .dataview {
        
    }

</style>
