<template>
    <section class="cases" v-if="items">
        <header class="cases-header">
            <h1 v-if="!urlQuery && !status_expired">Alle sager</h1>
            <h1 v-if="urlQuery && !status_expired">Søgeresultater</h1>
            <h1 v-if="status_expired">Udgåede sager</h1>
            <search />
            <fieldset class="expired-case">
                <input type="checkbox" id="field-status-expired" v-model="status_expired" @click="expiredItems()">
                <label for="field-status-expired">Udgåede sager</label>
            </fieldset>
        </header>
        <table v-if="items.length > 0">
            <thead>
                <tr>
                    <th>
                        Status
                    </th>
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
                        <span class="status-expired" v-if="i.expired === true">Udgået</span>
                        <span class="status-active" v-if="i.expired === false">Aktiv</span>
                    </td>
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
    import Search from '../search/Search.vue'

    export default {

        components: {
            Search
        },
        data: function() {
            return {
                cas: null,
                items: null,
                status_expired: false
            }
        },
        computed: {
            urlQuery: function() {
                return this.$route.params.query ? this.$route.params.query: false
            }
        },
        watch: {
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
                axios.get('/cases/?expired=false')
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
                } else {
                    this.fetchCases()
                }
            },
            expiredItems: function() {
                if (this.status_expired === false) {
                    axios.get(`/cases/?expired=true`)
                    .then(res => {
                        this.items = res.data
                    })
                } else {
                    this.fetchCases()
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

    .cases .search {
        margin: 0 2rem;
    }

    .cases .expired-case {
        margin: 0 0rem;
    }

    .cases .status-expired {
        background-color: var(--danger);
        color: white;
        padding: .25rem;
    }

    .cases .status-active {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

</style>
