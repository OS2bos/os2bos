<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div class="search-filter appropriation-search-filters">
        <form @submit.prevent>
            <fieldset class="filter-fields">

                <div class="filter-field">
                    <label for="field-sbsysid">SBSYS ID</label>
                    <input type="search" id="field-sbsysid" v-model="case__sbsys_id">
                </div>

                <div class="filter-field">
                    <label for="field-cpr">Hovedsag CPR</label>
                    <input type="search" id="field-cpr" v-model="case__cpr_number">
                </div>

                <div class="filter-field">
                    <label for="field-team">Team</label>
                    <list-picker 
                        v-if="teams"
                        :dom-id="'field-team'" 
                        :selected-id="case__case_worker__team"
                        :list="teams"
                        @selection="changeTeam"
                        display-key="name"
                    />
                </div>
            
                <div class="filter-field">
                    <label for="field-case-worker">Sagsbehandler</label>
                    <list-picker 
                        v-if="users"
                        :dom-id="'field-case-worker'" 
                        :selected-id="case__case_worker"
                        :list="users"
                        @selection="changeWorker"
                        display-key="fullname"
                    />
                </div>

                <div class="filter-field">
                    <label for="field-section">Bevilling efter §</label>
                    <list-picker
                        v-if="sections"
                        class="resize"
                        :dom-id="'field-section'" 
                        :selected-id="section"
                        :list="sections"
                        @selection="changeSection"
                        display-key="paragraph"
                        display-key2="text"
                    />
                </div>

                <div class="filter-field">
                    <label for="field-main-act">Hovedydelse</label>
                    <list-picker 
                        v-if="appr_main_acts"
                        class="resize"
                        :dom-id="'field-main-act'" 
                        :selected-id="main_activity__details__id"
                        :list="appr_main_acts"
                        @selection="changeMainAct"
                        display-key="name"
                    />
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
    import Timeout from '../mixins/Timeout.js'

    export default {
        components: {
            ListPicker
        },
        mixins: [
            Timeout
        ],
        computed: {
            cas: function() {
                return this.$store.getters.getCase
            },
            apprs: function() {
                return this.$store.getters.getAppropriations
            },
            users: function() {
                return this.$store.getters.getUsers
            },
            teams: function() {
                return this.$store.getters.getTeams
            },
            sections: function() {
                return this.$store.getters.getSections
            },
            appr_main_acts: function() {
                let actList = this.$store.getters.getActivityDetails.filter(act => act.main_activity_for.length > 0)
                return actList
            },
            user: function() {
                let user = this.$store.getters.getUser
                if (user) {
                    this.$store.dispatch('fetchTeam', user.team)
                }
                return user
            },
            // Search filters:
            case__sbsys_id: {
                get: function() {
                    // Get search filter saved in store. Displays in input field via `v-model`
                    return this.$store.getters.getAppropriationSearchFilter('case__sbsys_id')
                },
                set: function(new_val) {
                    // When user changes value in input field, commit the new value
                    // The `commitValue` helper method has a debounce feature, in order to avoid request spamming.
                    // This method is handy for values that the user types into text fields.
                    this.commitValue('case__sbsys_id', new_val)
                }
            },
            case__cpr_number: {
                get: function() {
                    return this.$store.getters.getAppropriationSearchFilter('case__cpr_number')
                }, 
                set: function(new_val) {
                    this.commitValue('case__cpr_number', new_val)
                }
            },
            case__case_worker__team: function() {
                // `case__case_worker__team` only has a getter. values are updated via changeTeam method in listpicker component
                return this.$store.getters.getAppropriationSearchFilter('case__case_worker__team')
            },
            case__case_worker: function() {
                // `case__case_worker` only has a getter. values are updated via changeWorker method in listpicker component
                return this.$store.getters.getAppropriationSearchFilter('case__case_worker')
            },
            section: function() {
                // `section` only has a getter. values are updated via changeSection method in listpicker component
                return this.$store.getters.getAppropriationSearchFilter('section')
            },
            main_activity__details__id: function() {
                // `main_activity__details__id` only has a getter. values are updated via changeMainAct method in listpicker component
                return this.$store.getters.getAppropriationSearchFilter('main_activity__details__id')
            }
        },
        watch: {
            user: function(new_val, old_user) {
                if (new_val !== old_user) {
                    this.updateUser()
                }
            }
        },
        methods: {
            resetValues: function() {
                // Use the store action to reset values
                this.$store.dispatch('resetAppropriationSearchFilters', this.user.id)
                this.$store.commit('setAppropriationSearchFilter', {})
                location.reload()
            },
            commitValue: function(key, val) {
                // Handy helper method that both updates the value in store, 
                // dispatches a request to get an updated list of appropriations,
                // and is debounced to avoid API request spam.
                this.$store.commit('setAppropriationSearchFilter', {[key]: val})
                this.$store.dispatch('fetchAppropriations')
            },
            changeTeam: function(selection) {
                // Checks if anything has actually been changed and updates store values
                // + fetches an updated list of appropriations
                if (this.case__case_worker__team !== selection && this.case__case_worker__team || selection) {
                    this.$store.commit('setAppropriationSearchFilter', {'case__case_worker__team': selection})
                    this.$store.dispatch('fetchAppropriations')
                }
            },
            changeWorker: function(selection) {
                // Checks if anything has actually been changed and updates store values
                // + fetches an updated list of appropriations
                if (this.case__case_worker !== selection && this.case__case_worker || selection) {
                    this.$store.commit('setAppropriationSearchFilter', {'case__case_worker': selection})
                    this.$store.dispatch('fetchAppropriations')
                }
            },
            changeSection: function(selection) {
                // Checks if anything has actually been changed and updates store values
                // + fetches an updated list of appropriations
                if (this.section !== selection && this.section || selection) {
                    this.$store.commit('setAppropriationSearchFilter', {'section': selection})
                    this.$store.dispatch('fetchAppropriations')
                }
            },
            changeMainAct: function(selection) {
                // Checks if anything has actually been changed and updates store values
                // + fetches an updated list of appropriations
                if (this.main_activity__details__id !== selection && this.main_activity__details__id || selection) {
                    this.$store.commit('setAppropriationSearchFilter', {'main_activity__details__id': selection})
                    this.$store.dispatch('fetchAppropriations')
                }
            },
            updateUser: function() {
                // Start out by setting a default case worker unless a case worker has already been set
                // and getting a list of appropriations with only initial filters set.
                if (!this.case__case_worker && this.user.id) {
                    this.$store.commit('setAppropriationSearchFilter', {'case__case_worker': this.user.id})
                    this.$store.dispatch('fetchAppropriations', this.$route.query)
                }
            }
        },
        created: function() {

            // Set debounce on methods that are likely to be fired too often
            // (ie. while a user is typing into an input field)
            this.commitValue = this.debounce(this.commitValue, 400)

            // On first load, check URL params and set store filters accordingly
            const qry = this.$route.query
            if (qry.case__sbsys_id || qry.case__case_worker__team || qry.case__case_worker || qry.section || qry.main_activity__details__id) {
                this.$store.commit('setAppropriationSearchFilter', qry)
                this.$store.dispatch('fetchAppropriations')
            }

            // Start out by setting a case worker
            this.updateUser()

        }
    }
    
</script>

<style>

    .appropriation-search-filters .resize {
        max-width: 18.5rem;
    }

    .appropriation-search-filters .filter-actions {
        flex-grow: 1;
        text-align: right;
    }

</style>