<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="cases" v-if="cas">
        <header class="cases-header">
            <h1>Mine sager</h1>
            <button class="create" @click="$router.push('/case-create/')">+ Tilknyt hovedsag</button>
        </header>
        <table v-if="cas.length > 0">
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
                <tr v-for="c in cas" :key="c.id">
                    <td>
                        <span class="status-active" v-if="c.expired === false">Aktiv</span>
                    </td>
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
        computed: {
            user: function() {
                return this.$store.getters.getUser
            }
        },
        watch: {
            user: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                this.fetchCases(this.$route.params.id)
            },
            fetchCases: function(id) {
                if (this.user) {
                    axios.get(`/cases/?case_worker=${ this.user.id }&expired=false`)
                    .then(res => {
                        this.cas = res.data
                    })
                    .catch(err => console.log(err))
                }
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

    .cases .create {
        margin: 0 2rem;
    }

    .cases .status-active {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

</style>
