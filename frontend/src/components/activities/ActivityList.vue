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
                    <th style="text-align: right;">Udgift i år</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in acts" :key="a.id" :class="{'expected-row': a.status === 'EXPECTED'}">
                    <td>
                        <div v-html="statusLabel(a.status)"></div>
                    </td>
                    <td>
                        <router-link :to="`/activity/${ a.id }`">{{ activityId2name(a.details) }}</router-link>
                        <span v-if="a.activity_type === 'MAIN_ACTIVITY'" class="act-label">Hovedydelse</span>
                    </td>
                    <td></td>
                    <td>{{ displayDate(a.start_date) }}</td>
                    <td>{{ displayDate(a.end_date) }}</td>
                    <td style="text-align: right;">{{ a.total_cost_this_year }} kr</td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td style="font-weight: bold;">Samlet bevilget</td>
                    <td style="text-align: right; font-weight: bold;">
                        {{ appropriation.total_granted_this_year }} kr
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td class="expected">Samlet forventet</td>
                    <td class="expected" style="text-align: right;">
                        {{ appropriation.total_expected_this_year }} kr
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
        computed: {
            appropriation: function() {
                return this.$store.getters.getAppropriation
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

    .activities .expected-row > td,
    .activities .expected {
        background-color: hsl(var(--color3), 80%, 80%); 
    }

    .activities .act-label {
        opacity: .66;
        font-size: .85rem;
        margin: 0 1rem;
    }

</style>
