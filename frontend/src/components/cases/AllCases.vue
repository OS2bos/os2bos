<template>
    <section class="cases" v-if="items">
        <header class="cases-header">
            <h1 v-if="!urlQuery">Alle sager</h1>
            <h1 v-if="urlQuery">Søgeresultater</h1>
        </header>
        <table v-if="items.length > 0">
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
                </tr>
            </tbody>
            </template>
        </table>
        <p v-if="!urlQuery && items.length < 1">
            Der er ikke tilknyttet nogen sager
        </p>
        <p v-if="urlQuery && items.length < 1">
            Ingen resultater
        </p>
    </section>
</template>

<script>
    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'

    export default {

        data: function() {
            return {
                cas: null,
                items: null
            }
        },
        computed: {
            urlQuery: function() {
                return this.$route.params.query ? this.$route.params.query: false
            }
        },
        watch: {
          items: function() {
              this.$store.commit('setBreadcrumb', [
                  {
                      link: '/',
                      title: 'Mine sager'
                  }
              ])
          },
          urlQuery: function() {
              this.displayItems(this.$route.params.query)
          }
        },
        methods: {
            update: function() {
                this.fetchCases(this.$route.params.id)
                this.displayItems(this.$route.params.query)
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
            }, 
            displayItems: function() {
                if (this.$route.params.query) {
                    axios.get(`/cases/?cpr_number=${ this.$route.params.query }`)
                    .then(res => {
                        this.items = res.data
                    })
                }
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
