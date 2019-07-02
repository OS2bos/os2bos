<template>

    <section class="activities">
        <button class="activities-create-btn" title="Ny aktivitet" @click="$router.push(`/appropriation/${ apprId }/activity-create/`)">+ Tilføj ydelse</button>
        <table v-if="acts && acts.length > 0">
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Ydelse</th>
                    <th>Udbetales til</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th>Økonomi</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in acts" :key="a.id">
                    <td>
                        <div v-html="statusLabel(a.status)"></div>
                    </td>
                    <td><router-link :to="`/activity/${ a.id }`">{{ activityId2name(a.details) }}</router-link></td>
                    <td></td>
                    <td>{{ displayDate(a.start_date) }}</td>
                    <td>{{ displayDate(a.end_date) }}</td>
                    <td>ikke implementeret</td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td style="text-align: right;">Pr. måned</td>
                    <td>
                        ikke implementeret kr.
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td style="text-align: right;">Samlet sum</td>
                    <td>
                        <u>ikke implementeret kr.</u>
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-if="!acts || acts.length < 1">Der er endnu ingen ydelser</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
    import { activityId2name, displayStatus } from '../filters/Labels.js'

    export default {

        props: [
            'apprId'
        ],
        data: function() {
            return {
                acts: null,
                pay: null
            }
        },
        methods: {
            update: function() {
                this.fetchActivities(this.$route.params.id)
            },
            fetchActivities: function() {
              axios.get(`/activities/?appropriation=${ this.apprId }`)
                .then(res => {
                    this.acts = res.data
                    axios.get(`/payment_schedules/?activities=${ this.acts.payment_plan  }`)
                        .then(resp => {
                            this.pay = resp.data
                        })
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2js(dt)
            },
            activityId2name: function(id) {
                return activityId2name(id)
            },
            statusLabel: function(status) {
                return displayStatus(status)
            }
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

</style>
