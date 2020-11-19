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
                    <input type="search" id="field-sbsysid" v-model="sbsys_id" @input="changeSbsysId">
                </div>
                
                <div class="filter-field">
                    <label for="field-cpr">CPR-nr</label>
                    <input type="search" id="field-cpr" v-model="cpr_number" @input="changeCprNumber">
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
                this.$store.commit('setCaseSearchFilter', {key: 'sbsys_id', val: new_val})
                this.$store.dispatch('fetchCases')
            }
        },
        cpr_number: function() {
            return this.$store.getters.getCaseSearchFilter('cpr_number')
        },
        expired: function() {
            return this.$store.getters.getCaseSearchFilter('expired')
        },
        team: function() {
            return this.$store.getters.getCaseSearchFilter('team')
        },
        case_worker: function() {
            return this.$store.getters.getCaseSearchFilter('case_worker')
        }
    },
    watch: {
        $route: function(to, from) {
            
        }
    },
    methods: {
        resetValues: function() {
            // TODO: Reset values
        },
        changeCprNumber: function(ev) {
            console.log('fire cpr number change')
            this.$store.commit('setCaseSearchFilter', {key: 'cpr_number', val: ev.target.value})
            this.$store.dispatch('fetchCases')
        },
        changeSbsysId: function(ev) {
            //this.$store.commit('setCaseSearchFilter', {key: 'sbsys_id', val: ev.target.value})
            //this.$store.dispatch('fetchCases')
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