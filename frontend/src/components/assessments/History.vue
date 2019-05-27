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
                        ikke implementeret {{ h.effort_stairs }}
                    </td>
                    <td>
                        ikke implementeret {{ h.scaling_staircase }}
                    </td>
                    <td>
                        ikke implementeret
                    </td>
                    <td>
                        {{ displayDate(h.modified)}}
                    </td>
                </tr>
            </tbody>
        </table>
    </section>
</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'

    export default {

        data: function() {
            return {
                his: null
            }
        },
        methods: {
            update: function() {
                this.fetchHistory(this.$route.params.id)
            },
            fetchHistory: function(id) {
                axios.get('/cases/')
                .then(res => {
                    this.his = res.data
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2js(dt)
            }
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

</style>