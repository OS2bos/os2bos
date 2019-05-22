<template>

    <section class="appropriations">
        <header class="appropriations-header">
            <h1>Foranstaltninger</h1>
            <button class="appropriation-create-btn" @click="createAppr()">+ Tilføj foranstaltning</button>
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
                        <router-link :to="`/appropriation/${ a.pk }`">
                            {{ a.sbsys_id }} 
                        </router-link>
                    </td>
                    <td>{{ a.activities.main_law_ref }}</td>
                    <td>{{ a.activities.main_activity_name }}</td>
                    <td>{{ a.activities.activities_count }}</td>
                    
                    <td><span class="status">{{ a.status }}</span></td>
                    <td>{{ new Date(a.created_date).toLocaleDateString() }}</td>
                    <td>{{ new Date(a.modified_date).toLocaleDateString() }}</td>
                    <td style="text-align: right">{{ a.payment.total_amount }} kr</td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td style="text-align: right">Samlet</td>
                    <td style="text-align: right"><strong>{{ total_amounts }}</strong> kr</td>
                </tr>
            </tbody>
        </table>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

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
            }
        },
        created: function() {
            this.fetchAppropriations()
        }
    }
    
</script>

<style>

    .appropriations {
        margin: 1rem;
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
