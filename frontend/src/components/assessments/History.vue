<template>
    <section>
        <h1>Historik</h1>
        <table>
            <thead>
                <tr>
                    <th>
                        Sagsbehandler
                    </th> 
                    <th>
                        Indsatstrappen
                    </th>
                    <th>
                        Skaleringstrappe
                    </th>
                    <th>
                        Bemærkning
                    </th>
                    <th>
                        Dato
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="h in his" :key="h.id">
                    <td>
                        <i class="material-icons">account_circle</i>
                        {{ h.case_worker }}
                    </td>
                    <td>
                        {{ displayEffortName(h.effort_step) }}
                    </td>
                    <td>
                        {{ h.scaling_step }}
                    </td>
                    <td>
                        Ikke implementeret
                    </td>
                    <td>
                        {{ displayDate(h.history_date)}}
                    </td>
                </tr>
            </tbody>
        </table>
    </section>
</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
    import { displayEffort } from '../filters/Labels.js'

    export default {

        props: [
            'caseObj'
        ],
        data: function() {
            return {
                his: null
            }
        },
        watch: {
            caseObj: {
                handler() {
                    this.fetchHistory(this.caseObj.id)
                },
                deep: true
            }
        },
        methods: {
            fetchHistory: function(id) {
                axios.get(`/cases/${ id }/history`)
                .then(res => {
                    this.his = res.data
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2js(dt)
            },
            displayEffortName: function(str) {
                return displayEffort(str)
            }
        },
        created: function() {
            this.fetchHistory(this.caseObj.id)
        }
    }
    
</script>

<style>

</style>