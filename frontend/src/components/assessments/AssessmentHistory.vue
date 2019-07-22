<template>
    <section class="assessment-history">
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
                        Supplerende information
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
                        {{ displayUserName(h.case_worker) }}
                    </td>
                    <td :class="`step-${h.effort_step}`">
                        {{ displayEffortName(h.effort_step) }}
                    </td>
                    <td :class="`step-${h.scaling_step}`">
                        {{ h.scaling_step }}
                    </td>
                    <td>
                        {{ h.history_change_reason }}
                    </td>
                    <td>
                        {{ displayDate(h.history_date) }}
                    </td>
                </tr>
            </tbody>
        </table>
    </section>
</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
    import { displayEffort, userId2name } from '../filters/Labels.js'

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
            },
            displayUserName: function(id) {
                return userId2name(id)
            }
        },
        created: function() {
            this.fetchHistory(this.caseObj.id)
        }
    }
    
</script>

<style>

    .assessment-history .step-STEP_ONE {
        color: hsl(100, 100%, 33%);   
    }

    .assessment-history .step-STEP_TWO {
        color: hsl(80, 100%, 33%);   
    }

    .assessment-history .step-STEP_THREE {
        color: hsl(60, 100%, 33%);   
    }

    .assessment-history .step-STEP_FOUR {
        color: hsl(40, 100%, 33%);   
    }

    .assessment-history .step-STEP_FIVE {
        color: hsl(20, 100%, 33%);   
    }

    .assessment-history .step-STEP_SIX {
        color: hsl(0, 100%, 33%);   
    }

    .assessment-history .step-1 {
        color: hsl(100, 100%, 33%);   
    }

    .assessment-history .step-2 {
        color: hsl(80, 100%, 33%);   
    }

    .assessment-history .step-3 {
        color: hsl(60, 100%, 33%);   
    }

    .assessment-history .step-4 {
        color: hsl(40, 100%, 33%);   
    }

    .assessment-history .step-5 {
        color: hsl(20, 100%, 33%);   
    }

    .assessment-history .step-6 {
        color: hsl(0, 100%, 33%);   
    }

</style>