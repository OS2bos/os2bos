<template>
    
    <div class="case-search">

        <div class="case-search-list">
            <h1>Sager</h1>
            <table v-if="cases.length > 0">
                <thead>
                    <tr>
                        <th style="width: 4.5rem;">
                            <input type="checkbox" id="field-select-all">
                            <label for="field-select-all" title="Vælg alle"></label>
                        </th>
                        <th style="width: 6rem;">Status</th>
                        <th>SBSYS-hovedsag</th> 
                        <th>Borger</th>
                        <th>Ændret</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="c in cases" :key="c.id">
                        <td style="width: 4.5rem;">
                            <input type="checkbox" :id="`field-select-${ c.id }`">
                            <label title="Vælg alle" :for="`field-select-${ c.id }`"></label>
                        </td>
                        <td style="width: 6rem;">
                            <div class="mini-label" v-if="c.expired === false">
                                <span class="label label-GRANTED">Aktiv</span>
                            </div>
                        </td>
                        <td>
                            <i class="material-icons">folder_shared</i>
                            <router-link :to="`/case/${ c.id }`">
                                {{ c.sbsys_id }}
                            </router-link>
                        </td>
                        <td>
                            {{ c.cpr_number }}, {{ c.name }}
                        </td>
                        <td class="nowrap">
                            {{ displayDate(c.modified) }}
                        </td>
                    </tr>
                </tbody>
            </table>
            <p v-if="cases.length < 1">
                Kunne ikke finde nogen sager
            </p>
        </div>

        <div class="case-search-filters">
            <h2>Filtre</h2>
            <form>
                <fieldset>

                    <label for="field-cpr">CPR-nr</label>
                    <input type="search" @input="changeCpr()" id="field-cpr" v-model="field_cpr">

                    <label for="field-team">Team</label>
                    <list-picker 
                        :dom-id="'field-team'" 
                        :selected-id="field_team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name" />
                
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        :dom-id="'field-case-worker'" 
                        :selected-id="field_case_worker"
                        :list="users"
                        @selection="changeWorker"
                        display-key="fullname" />
                
                </fieldset>
                <fieldset>

                    <input type="checkbox" v-model="field_expired" id="field-expired" @change="changeExpired()">
                    <label for="field-expired">Udgåede sager</label>

                </fieldset>
            </form>
        </div>

    </div>

</template>

<script>

    import { json2js } from '../filters/Date.js'
    import ListPicker from '../forms/ListPicker.vue'

    export default {

        components: {
            ListPicker
        },
        data: function() {
            return {
                field_cpr: null,
                field_case_worker: null,
                field_team: null,
                field_expired: false
            }
        },
        computed: {
            cases: function() {
                return this.$store.getters.getCases
            },
            users: function() {
                return this.$store.getters.getUsers
            },
            teams: function() {
                return this.$store.getters.getTeams
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchCases', this.$route.query)
            },
            displayDate: function(date) {
                return json2js(date)
            },
            changeCpr: function() {
                let cpr = this.field_cpr.replace('-','')
                if (cpr.length === 10) {
                    this.$route.query.cpr_number = this.cpr
                    this.update()
                }
            },
            changeWorker: function(worker_id) {
                this.$route.query.case_worker = worker_id
                this.update()
            },
            changeTeam: function(team_id) {
                this.$route.query.team = team_id
                this.update()
            },
            changeExpired: function() {
                this.$route.query.expired = this.field_expired
                this.update()
            }
        },
        created: function() {
            this.update()
        }

    }

</script>

<style>

    .case-search {
        padding: 2rem;
        display: flex;
        flex-flow: row nowrap;
    }

    .case-search-list {
        order: 2;
    }

    .case-search-list .more .material-icons {
        margin: 0;
    }

    .case-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 1rem;
        margin-right: 2rem;
    }

    .case-search-filters h2,
    .case-search-filters form {
        padding: 0;
    }

</style>