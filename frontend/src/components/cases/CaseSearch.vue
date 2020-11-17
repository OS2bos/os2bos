<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="search-filter case-search-filters">
        <form @submit.prevent>
            <fieldset class="filter-fields">

                <div class="filter-field">
                    <label for="field-sbsysid">SBSYS ID</label>
                    <input type="search" id="field-sbsysid" v-model="sbsys_id">
                </div>
                
                <div class="filter-field">
                    <label for="field-cpr">CPR-nr</label>
                    <input type="search" id="field-cpr" v-model="cpr_number">
                </div>

                <div class="filter-field">
                    <label for="field-team">Team</label>
                    <list-picker 
                        v-if="teams"
                        :dom-id="'field-team'" 
                        :selected-id="team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name" />
                </div>

                <div class="filter-field">
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        v-if="users"
                        :dom-id="'field-case-worker'" 
                        :selected-id="case_worker"
                        :list="users"
                        @selection="changeCaseWorker"
                        display-key="fullname" />
                </div>
                
            </fieldset>

            <fieldset class="filter-fields radio-filters">
                <div class="filter-field">
                    <input type="radio" v-model="expired" id="field-expired-1" :value="null">
                    <label for="field-expired-1">Aktive og lukkede sager</label>
                </div>
                <div class="filter-field">
                    <input type="radio" v-model="expired" id="field-expired-2" :value="false">
                    <label for="field-expired-2">Kun aktive sager</label>
                </div>
                <div class="filter-field">
                    <input type="radio" v-model="expired" id="field-expired-3" :value="true">
                    <label for="field-expired-3">Kun lukkede sager</label>
                </div>

            </fieldset>

            <fieldset class="filter-fields filter-actions">
                <button class="filter-reset" type="reset" @click="resetValues">Nulstil</button>
            </fieldset>
        </form>
    </div>
</template>

<script>
import ListPicker from '../forms/ListPicker.vue'

// Debounce function allows for functions to wait for user to stop making inputs
const debounce = function(fn, delay) {
    let timeoutID = null
    return function () {
        clearTimeout(timeoutID)
        const args = arguments
        const that = this
        timeoutID = setTimeout(function () {
            fn.apply(that, args)
        }, delay)
    }
}

/*

    When url changes, update models
    when model changes (by user input), update url
*/
export default {
    components: {
        ListPicker
    },
    data: function() {
        return {
            sbsys_id: null,
            cpr_number: null,
            expired: null,
            team: null,
            case_worker: null,
            query: {}
        }
    },
    computed: {
        teams: function() {
            return this.$store.getters.getTeams
        },
        users: function() {
            return this.$store.getters.getUsers
        },
        search_filters: function() {
            return this.$store.getters.getCaseSearchFilters
        },
        user: function() {
            return this.$store.getters.getUser
        }
    },
    watch: {
        $route: function(to, from) {
            if (to !== from) {
                this.getValuesFromUrl()
            }
        },
        sbsys_id: debounce(function(new_val) {
            this.postValuesToUrl('sbsys_id', new_val)
        }, 400),
        cpr_number: debounce(function(new_val) {
            let newer_val = null
            if (new_val) {
                newer_val = new_val.replace('-', '')
            }
            this.postValuesToUrl('cpr_number', newer_val)
        }, 400),
        expired: function(new_val) {
            this.postValuesToUrl('expired', new_val)
        },
        team: function(new_val) {
            this.postValuesToUrl('team', new_val)
        },
        case_worker: function(new_val) {
            this.postValuesToUrl('case_worker', new_val)
        }
    },
    methods: {
        postValuesToUrl: function(key, val) {
            if (val !== this.$route.query[key]) {
                this.$store.commit('setCaseSearchFilter', { key, val })
                this.query[key] = val
                this.$router.push({ path: '/cases', query: this.query })
            }
        },
        getValuesFromUrl: function() {   
            this.checkUrlOrState('sbsys_id')
            this.checkUrlOrState('cpr_number')
            this.checkUrlOrState('expired')
            this.checkUrlOrState('team')
            this.checkUrlOrState('case_worker')
        },
        checkUrlOrState: function(key) {
            if (this.$route.query[key]) {
                this[key] = this.$route.query[key]
            } else if (this.search_filters[key]) {
                this[key] = this.search_filters[key]
            } else {
                this.case_worker = this.user.id
            }
        },
        resetValues: function() {
            this.sbsys_id = null
            this.cpr_number = null
            this.expired = null
            this.team = null
            this.case_worker = this.user.id
        },
        changeCaseWorker: function(selection) {
            this.case_worker = selection
        },
        changeTeam: function(selection) {
            this.team = selection
        }
    },
    created: function() {
        this.getValuesFromUrl()
    }
}
</script>

<style>

.case-search-filters .radio-filters {
    margin-top: 1rem;
}

.case-search-filters .filter-actions {
    flex-grow: 1;
    text-align: right;
}

</style>