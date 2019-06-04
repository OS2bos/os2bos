<template>

    <section class="appropriations">
        <header class="appropriations-header">
            <h1>Foranstaltninger</h1>
            <button class="appropriation-create-btn" @click="$router.push('approriation-create')">+ Opret bevillingsskrivelse</button>
        </header>
        <table class="appropriation-list" v-if="apprs.length > 0">
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
                <tr v-for="a in apprs" :key="a.id">
                    <td>    
                        <i class="material-icons">folder_open</i>
                        <router-link :to="`/appropriation/${ a.id }`">
                            {{ a.sbsys_id }} 
                        </router-link>
                    </td>
                    <td>ikke implementeret</td>
                    <td>§ {{ a.section }}</td>
                    <td>ikke implementeret</td>
                    
                    <td><span class="status">{{ a.status }}</span></td>
                    <td>{{ displayDate(a.created) }}</td>
                    <td>{{ displayDate(a.modified) }}</td>
                    <td style="text-align: right">ikke implementeret</td>
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
        <p v-if="apprs.length < 1">Der er endnu ingen bevillingsskrivelser</p>
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
                    //return total + a.payment.total_amount
                }
                if (this.apprs) {
                    return this.apprs.reduce(getTotal, 0)
                }
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
            // createAppr: function() {
            //     axios.post('/appropriations/', {
                    
            //     }) // POST new empty appropriation
            //     .then(res => {
            //         this.$router.push(`/appropriation-create/${ res.data.id }`) // Navigate to new appropriation page
            //     })
            //     .catch(err => console.log(err))
            // },
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

</style>
