<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


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
                    <th style="width: 5.5rem;">Status</th>
                    <th>SBSYS-hovedsag</th> 
                    <th>Borger</th>
                    <th>Ændret</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="i in items" :key="i.id">
                    <td style="width: 5.5rem;">
                        <div class="mini-label" v-if="i.expired === false">
                            <span class="label label-GRANTED">Aktiv</span>
                        </div>
                        <div class="mini-label" v-if="i.expired === true">
                            <span class="label label-DISCONTINUED">Udgået</span>
                        </div>
                    </td>
                    <td>
                        <i class="material-icons">folder_shared</i>
                        <router-link :to="`/case/${ i.id }`">
                            {{ i.sbsys_id }}
                        </router-link>
                    </td>
                    <td>
                        {{ i.cpr_number }}, {{ i.name }}
                    </td>
                    <td class="nowrap">
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
    import { json2jsDate } from '../filters/Date.js'
    import Search from '../search/Search.vue'

    export default {

        components: {
            Search
        },
        data: function() {
            return {
                cas: null,
                items: [],
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
              this.update()
          }
        },
        methods: {
            update: function() {
                if (this.$route.params.query) {
                    this.displayItems(this.$route.params.query)
                } else {
                    this.fetchCases(this.$route.params.id)
                }
            },
            fetchCases: function(id) {
                axios.get('/cases/?expired=false')
                .then(res => {
                    this.items = res.data
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            }, 
            displayItems: function() {
                axios.get(`/cases/?cpr_number=${ this.$route.params.query }`)
                .then(res => {
                    this.items = res.data
                })
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
