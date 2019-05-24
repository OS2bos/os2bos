<template>
    <section>
        <h1>Historik</h1>
        <table>
            <thead>
                <tr>
                    <td>
                        Sagsbehandler
                    </td> 
                    <td>
                        Indsatstrappen
                    </td>
                    <td>
                        Skaleringstrappe
                    </td>
                    <td>
                        Dato
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="h in his" :key="h.pk">
                    <td>
                        {{ h.case_management.case_worker }}
                    </td>
                    <td>
                        {{ h.effort_stairs }}
                    </td>
                    <td>
                        {{ h.scaling_staircase }}
                    </td>
                    <td>
                        {{ h.modified }}
                    </td>
                </tr>
            </tbody>
        </table>
    </section>
</template>

<script>

    import axios from '../http/Http.js'

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
                axios.get('../../case-data.json')
                .then(res => {
                    this.his = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

</style>