<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


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
                    <td :class="`step-effort-${h.effort_step}`">
                        {{ displayEffortName(h.effort_step) }}
                    </td>
                    <td :class="`step-scale-${h.scaling_step}`">
                        {{ h.scaling_step }}
                    </td>
                    <td>
                        {{ h.assessment_comment }}
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

    
    .assessment-history .step-effort-1 {
        color: hsl(100, 100%, 33%);   
    }

    .assessment-history .step-effort-2 {
        color: hsl(80, 100%, 33%);   
    }

    .assessment-history .step-effort-3 {
        color: hsl(60, 100%, 33%);   
    }

    .assessment-history .step-effort-4 {
        color: hsl(40, 100%, 33%);   
    }

    .assessment-history .step-effort-5 {
        color: hsl(20, 100%, 33%);   
    }

    .assessment-history .step-effort-6 {
        color: hsl(0, 100%, 33%);   
    }

    .assessment-history .step-scale-1 {
        color: hsl(0, 100%, 33%);   
    }

    .assessment-history .step-scale-2 {
        color: hsl(20, 100%, 33%);   
    }

    .assessment-history .step-scale-3 {
        color: hsl(30, 100%, 33%);   
    }

    .assessment-history .step-scale-4 {
        color: hsl(40, 100%, 33%);   
    }

    .assessment-history .step-scale-5 {
        color: hsl(50, 100%, 33%);   
    }

    .assessment-history .step-scale-6 {
        color: hsl(60, 100%, 33%);   
    }

    .assessment-history .step-scale-7 {
        color: hsl(70, 100%, 33%);   
    }

    .assessment-history .step-scale-8 {
        color: hsl(80, 100%, 33%);   
    }

    .assessment-history .step-scale-9 {
        color: hsl(90, 100%, 33%);   
    }

    .assessment-history .step-scale-10 {
        color: hsl(100, 100%, 33%);   
    }

</style>
