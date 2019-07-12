<template>
    <section class="cases" v-if="items">
        <header class="cases-header">
            <h1>Udgåede sager</h1>
        </header>
        <table>
            <template>
            <thead>
                <tr>
                    <th>
                        SBSYS-hovedsag nr.
                    </th> 
                    <th>
                        Borger
                    </th>
                    <th>
                        Ændret
                    </th>
                     <th>
                        Status
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="i in items" :key="i.id">
                    <td>
                      <i class="material-icons">folder_shared</i>
                      <router-link :to="`/case/${ i.id }`">
                          {{ i.sbsys_id }}
                      </router-link>
                    </td>
                    <td>
                      {{ i.cpr_number }} - {{ i.name }}
                    </td>
                    <td>
                      {{ displayDate(i.modified) }}
                    </td>
                    <td>
                      Udgået
                    </td>
                </tr>
            </tbody>
            </template>
        </table>
        <p v-if="items.length < 1">
            Der er ikke tilknyttet nogen udgåede sager
        </p>
    </section>
</template>

<script>
    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'

    export default {

        data: function() {
            return {
                items: null
            }
        },
        methods: {
            update: function() {
                this.fetchCases(this.$route.params.id)
            },
            fetchCases: function(id) {
                axios.get('/cases/')
                .then(res => {
                    this.items = res.data

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

    .cases {
        margin: 0 2rem 2rem;
    }

    .cases-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

</style>
