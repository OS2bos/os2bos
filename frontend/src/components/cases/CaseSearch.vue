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
                        :selected-id="case_worker__team"
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
                <button class="filter-reset" type="button" @click="resetValues">Nulstil filtre</button>
            </fieldset>
        </form>
    </div>
</template>

<script>
import ListPicker from '../forms/ListPicker.vue'
import Timeout from '../mixins/Timeout.js'

export default {
    components: {
        ListPicker
    },
    mixins: [
        Timeout
    ],
    computed: {
        teams: function() {
            return this.$store.getters.getTeams
        },
        users: function() {
            return this.$store.getters.getUsers
        },
        user: function() {
            return this.$store.getters.getUser
        },
        // Search filters:
        sbsys_id: {
            get: function() {
                // Get search filter saved in store. Displays in input field via `v-model`
                return this.$store.getters.getCaseSearchFilter('sbsys_id')
            },
            set: function(new_val) {
                // When user changes value in input field, commit the new value
                // The `commitValue` helper method has a debounce feature, in order to avoid request spamming.
                // This method is handy for values that the user types into text fields.
                this.commitValue('sbsys_id', new_val)
            }
        },
        cpr_number: {
            get: function() {
                return this.$store.getters.getCaseSearchFilter('cpr_number')
            }, 
            set: function(new_val) {
                this.commitValue('cpr_number', new_val)
            }
        },
        expired: {
            get: function() {
                return this.$store.getters.getCaseSearchFilter('expired')
            }, 
            set: function(new_val) {
                // When user changes value in radio button, commit the new value
                // We don't use the `commitValue` helper method here.
                this.$store.commit('setCaseSearchFilter', {'expired': new_val})
                this.$store.dispatch('fetchCases')
            }
        },
        case_worker__team: function() {
            // `case_worker__team` only has a getter. values are updated via changeTeam method in listpicker component
            return this.$store.getters.getCaseSearchFilter('case_worker__team')
        },
        case_worker: function() {
            // `case_worker` only has a getter. values are updated via changeCaseWorker method in listpicker component
            return this.$store.getters.getCaseSearchFilter('case_worker')
        },
        hasUrlParams: function() {
            const qry = this.$route.query
            if (qry.sbsys_id || qry.hasOwnProperty('expired') && qry.expired !== null || qry.case_worker__team || qry.case_worker) {
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        resetValues: function() {
            // Reset values in vuex state
            this.$store.dispatch('resetCaseSearchFilters', this.user.id)
        },
        commitValue: function(key, val) {
            // Handy helper method that both updates the value in store, 
            // dispatches a request to get an updated list of cases,
            // and is debounced to avoid API request spam.
            this.$store.commit('setCaseSearchFilter', {[key]: val})
            this.$store.dispatch('fetchCases')
        },
        changeCaseWorker: function(selection) {
            // Checks if anything has actually been changed and updates store values
            // + fetches an updated list of cases
            if (this.case_worker !== selection && this.case_worker || selection) {
                this.$store.commit('setCaseSearchFilter', {'case_worker': selection})
                this.$store.dispatch('fetchCases')
            }
        },
        changeTeam: function(selection) {
            // Checks if anything has actually been changed and updates store values
            // + fetches an updated list of cases
            if (this.case_worker__team !== selection && this.case_worker__team || selection) {
                this.$store.commit('setCaseSearchFilter', {'case_worker__team': selection})
                this.$store.dispatch('fetchCases')
            }
        },
        updateUser: function() {
            // Start out by setting a default case worker if no url params are present
            // and getting a list of cases with only initial filters set.
            if (!this.hasUrlParams && this.user.id) { 
                this.$store.commit('setCaseSearchFilter', {'case_worker': this.user.id})
                this.$store.dispatch('fetchCases', this.$route.query)
            } else {
                this.$store.dispatch('fetchCases')
            }
        }
    },
    created: function() {

        // Set debounce on methods that are likely to be fired too often
        // (ie. while a user is typing into an input field)
        this.commitValue = this.debounce(this.commitValue, 400)

        // On first load, check URL params and set store filters accordingly
        if (this.hasUrlParams) {
            this.$store.commit('setCaseSearchFilter', this.$route.query)
        }
        
        // Start out by setting a case worker
        this.updateUser()
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