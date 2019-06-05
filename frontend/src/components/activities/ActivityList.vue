<template>

    <section class="activities">
        <button class="activities-create-btn" title="Ny aktivitet" @click="$router.push('/activity-create')">+ Tilføj ydelse</button>
        <table>
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
                        <span :class="`status-${ a.status }`">{{ a.status }}</span>
                    </td>
                    <td><router-link :to="`/activity/${ a.id }`">{{ activityId2name(a.service) }}</router-link></td>
                    <td>300578-2222 - Ukendt</td>
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
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
    import { activityId2name } from '../filters/Labels.js'

    export default {

        props: [
            'apprId'
        ],
        data: function() {
            return {
                acts: null   
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
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2js(dt)
            },
            activityId2name: function(id) {
                return activityId2name(id)
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

    .activities .status-GRANTED {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

    .activities .status-EXPECTED {
        background-color: var(--warning);
        color: white;
        padding: .25rem;
    }

    .total-sum {
        background-color: green;
        color: white;
        padding: .25rem;
    }

</style>
