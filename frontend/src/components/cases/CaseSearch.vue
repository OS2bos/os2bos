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
    data: function() {
        return {
            
        }
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
                return this.$store.getters.getCaseSearchFilter('sbsys_id')
            },
            set: function(new_val) {
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
                this.$store.commit('setCaseSearchFilter', {key: 'expired', val: new_val})
                this.$store.dispatch('fetchCases')
            }
        },
        team: function() {
            return this.$store.getters.getCaseSearchFilter('team')
        },
        case_worker: function() {
            return this.$store.getters.getCaseSearchFilter('case_worker')
        }
    },
    methods: {
        resetValues: function() {
            // TODO: Reset values
            this.$store.dispatch('resetCaseSearchFilters')
        },
        commitValue: function(key, val) {
            this.$store.commit('setCaseSearchFilter', {key: key, val: val})
            this.$store.dispatch('fetchCases')
        },
        changeCaseWorker: function(selection) {
            if (this.case_worker !== selection && this.case_worker || selection) {
                this.$store.commit('setCaseSearchFilter', {key: 'case_worker', val: selection})
                this.$store.dispatch('fetchCases')
            }
        },
        changeTeam: function(selection) {
            if (this.team !== selection && this.team || selection) {
                this.$store.commit('setCaseSearchFilter', {key: 'team', val: selection})
                this.$store.dispatch('fetchCases')
            }
        }
    },
    created: function() {
        this.$store.dispatch('fetchCases')

        // Set debounce on methods that are likely to be fired often (ie. while a user types input)
        this.commitValue = debounce(this.commitValue, 400)
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