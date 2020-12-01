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

// Debounce helper method lets a function await execution until it is no longer called again.
// Useful for waiting for a user to stop typing in an input field.
const debounce = function(func, wait) {
	let timeout
	return function() {
        let context = this, 
            args = arguments
		const later = function() {
			timeout = null
			func.apply(context, args)
		}
		clearTimeout(timeout)
		timeout = setTimeout(later, wait)
	}
}

export default {
    components: {
        ListPicker
    },
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
                this.$store.commit('setCaseSearchFilter', {key: 'expired', val: new_val})
                this.$store.dispatch('fetchCases')
            }
        },
        team: function() {
            // `team` only has a getter. values are updated via changeTeam method in listpicker component
            return this.$store.getters.getCaseSearchFilter('team')
        },
        case_worker: function() {
            // `case_worker` only has a getter. values are updated via changeCaseWorker method in listpicker component
            return this.$store.getters.getCaseSearchFilter('case_worker')
        }
    },
    watch: {
        user: function(new_user, old_user) {
            // We need to wait for a user to appear before we can initialise the component
            if (new_user !== old_user) {
                this.update()
            }
        }
    },  
    methods: {
        resetValues: function() {
            // Use the store action to reset values
            this.$store.dispatch('resetCaseSearchFilters')
        },
        commitValue: function(key, val) {
            // Handy helper method that both updates the value in store, 
            // dispatches a request to get an updated list of cases,
            // and is debounced to avoid API request spam.
            this.$store.commit('setCaseSearchFilter', {key: key, val: val})
            this.$store.dispatch('fetchCases')
        },
        changeCaseWorker: function(selection) {
            // Checks if anything has actually been changed and updates store values
            // + fetches an updated list of cases
            if (this.case_worker !== selection && this.case_worker || selection) {
                this.$store.commit('setCaseSearchFilter', {key: 'case_worker', val: selection})
                this.$store.dispatch('fetchCases')
            }
        },
        changeTeam: function(selection) {
            // Checks if anything has actually been changed and updates store values
            // + fetches an updated list of cases
            if (this.team !== selection && this.team || selection) {
                this.$store.commit('setCaseSearchFilter', {key: 'team', val: selection})
                this.$store.dispatch('fetchCases')
            }
        },
        update: function() {
            // Start out by setting a default case worker unless a case worker has already been set
            // and getting a list of cases with only initial filters set.
            if (!this.case_worker) {
                this.$store.commit('setCaseSearchFilter', {key: 'case_worker', val: this.user.id})
            }
            this.$store.dispatch('fetchCases')
        }
    },
    created: function() {

        // Set debounce on methods that are likely to be fired too often
        // (ie. while a user is typing into an input field)
        this.commitValue = debounce(this.commitValue, 400)

        // On first load, check URL params and set store filters accordingly
        if (this.$route.query.sbsys_id) {
            this.$store.commit('setCaseSearchFilter', {key: 'sbsys_id', val: this.$route.query.sbsys_id})
        }
        if (this.$route.query.expired) {
            this.$store.commit('setCaseSearchFilter', {key: 'expired', val: this.$route.query.expired})
        }
        if (this.$route.query.team) {
            this.$store.commit('setCaseSearchFilter', {key: 'team', val: this.$route.query.team})
        }
        if (this.$route.query.case_worker) {
            this.$store.commit('setCaseSearchFilter', {key: 'case_worker', val: this.$route.query.case_worker})
        }
        this.$store.dispatch('fetchCases')
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