<template>

    <section class="appropriations">
        <header class="appropriations-header">
            <h1>Foranstaltninger</h1>
            <button class="appropriation-create-btn" @click="$router.push(`/case/${ caseId }/appropriation-create/`)">+ Opret bevillingsskrivelse</button>
        </header>
        <table class="appropriation-list" v-if="apprs && apprs.length > 0">
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
                    <td>§ {{ displaySection(a.section) }}</td>
                    <td>ikke implementeret</td>
                    <td><div v-html="statusLabel(a.status)"></div></td>
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
        <p v-if="!apprs || apprs.length < 1">Der er endnu ingen bevillingsskrivelser</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
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
            displayDate: function(dt) {
                return json2js(dt)
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

</style>
