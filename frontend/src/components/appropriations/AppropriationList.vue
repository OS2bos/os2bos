<template>

    <section class="appropriations">
        <header class="appropriations-header">
            <h1>Foranstaltninger</h1>
            <button class="appropriation-create-btn" @click="createAppr()">+ Tilknyt foranstaltningssag</button>
        </header>
        <table>
            <thead>
                <tr>
                    <th>Foranstaltningssag</th>
                    <th>Foranstaltningsudgift</th>
                    <th>Aktivitet</th>
                    <th>Følgeudgift</th>
                    <th>Status</th>
                    <th>Oprettet</th>
                    <th>Senest ændret</th>
                    <th style="text-align: right">Økonomi</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in apprs" :key="a[0]">
                    <td>    
                        <i class="material-icons">folder_open</i>
                        <router-link :to="`/appropriation/${ a.pk }`">
                            {{ a.sbsys_id }} 
                        </router-link>
                    </td>
                    <td>{{ a.activities.main_law_ref }}</td>
                    <td>{{ a.activities.main_activity_name }}</td>
                    <td>{{ a.activities.activities_count }}</td>
                    
                    <td><span class="status">{{ a.status }}</span></td>
                    <td>{{ displayDate(a.created_date) }}</td>
                    <td>{{ displayDate(a.modified_date) }}</td>
                    <td style="text-align: right">{{ a.payment.total_amount }} kr</td>
                </tr>
                <tr>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="border: none;"></td>
                    <td style="text-align: right; border: none;">Samlet</td>
                    <td style="text-align: right; border: none;">{{ total_amounts }} kr</td>
                </tr>
            </tbody>
        </table>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'

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
            total_amounts: function() {
                function getTotal(total, a) {
                    console.log(total)
                    console.log(a.payment.total_amount)
                    return total + a.payment.total_amount
                }
                if (this.apprs) {
                    return this.apprs.reduce(getTotal, 0)
                }
            }
        },
        methods: {
            fetchAppropriations: function(case_id) {
                axios.get('../../appropriation-list-data.json')
                .then(res => {
                    this.apprs = res.data
                })
                .catch(err => console.log(err))
            },
            createAppr: function() {
                axios.post('/') // POST new empty appropriation
                .then(res => {
                    this.$router.push(`/appropriation/${ res.data.pk }`) // Navigate to new appropriation page
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2js(dt)
            }
        },
        created: function() {
            this.fetchAppropriations()
        }
    }
    
</script>

<style>

    .appropriations {
        margin: 1rem 0 2rem;
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

</style>
