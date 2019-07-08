<template>
    <section class="cases" v-if="cas">
        <header class="cases-header">
            <h1>Alle sager</h1>
        </header>
        <table v-if="cas.length > 0">
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
                <tr v-for="c in cas" :key="c.id">
                    <td>
                        <i class="material-icons">folder_shared</i>
                        <router-link :to="`/case/${ c.id }`">
                            {{ c.sbsys_id }}
                        </router-link>
                    </td>
                    <td>
                        {{ c.cpr_number }} - {{ c.name }}
                    </td>
                    <td>
                        {{ displayDate(c.modified) }}
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-if="cas.length < 1">
            Der er ikke tilknyttet nogen sager
        </p>
    </section>
</template>

<script>
    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'

    export default {

        data: function() {
            return {
                cas: null
            }
        },
        watch: {
          cas: function() {
              this.$store.commit('setBreadcrumb', [
                  {
                      link: '/',
                      title: 'Mine sager'
                  },
                  {
                      link: false,
                      title: "Alle sager"
                  }
              ])
          }
        },
        methods: {
            update: function() {
                this.fetchCases(this.$route.params.id)
            },
            fetchCases: function(id) {
                axios.get('/cases/')
                .then(res => {
                    this.cas = res.data
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
