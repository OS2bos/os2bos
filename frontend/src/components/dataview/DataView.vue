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
