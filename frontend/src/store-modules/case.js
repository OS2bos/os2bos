/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import Vue from 'vue'

const makeQueryString = function(state, show_sensitive_data) {
    let q = ''
    if (state.filters.sbsys_id) {
        q = q + `sbsys_id=${ state.filters.sbsys_id }&`
    }
    if (show_sensitive_data && state.filters.cpr_number) {
        q = q + `cpr_number=${ state.filters.cpr_number }&`
    }
    if (state.filters.expired) {
        q = q + `expired=${ state.filters.expired }&`
    }
    if (state.filters.team) {
        q = q + `team=${ state.filters.team }&`
    }
    if (state.filters.case_worker) {
        q = q + `case_worker=${ state.filters.case_worker }`
    }
    return q
}

/**
 * Vuex store methods for cases
 * @name state_case
 */
const state = {
    cases: null,
    main_case: null,
    // Search filters:
    filters: {
        sbsys_id: null,
        cpr_number: null,
        case_worker: null,
        team: null,
        expired: null
    }
}

const getters = {
    /**
     * Get list of cases currently in the store.
     * @name getCases
     * @returns {array} List of cases
     * @example this.$store.getters.getCases()
     * @memberof state_case
     */
    getCases (state) {
        return state.cases ? state.cases : false
    },
    /**
     * Get case info currently in the store.
     * @name getCase
     * @returns {object} A single case object
     * @example this.$store.getters.getCase()
     * @memberof state_case
     */
    getCase (state) {
        return state.main_case ? state.main_case : false
    },
    /**
     * Get case search filter value from store.
     * @name getCaseSearchFilter
     * @param {string} filter_key A string corresponding to a property key in state.filters
     * @returns {any} Whatever is stored in state.filters[filter_key]
     * @example this.$store.getters.getCaseSearchFilter('case_worker')
     * @memberof state_case
     */
    getCaseSearchFilter: (state) => (filter_key) => {
        return state.filters[filter_key]
    }
}

const mutations = {
    setCases (state, cases) {
        state.cases = cases
    },
    setCase (state, main_case) {
        state.main_case = main_case
    },
    clearCase (state) {
        state.main_case = null
    },
    /**
     * Set value of a property in state.filters
     * Also updates URL to expose query string
     * @name setCaseSearchFilter
     * @param {object} obj An object with key/value pairs corresponding to the property change. `key` is always a String
     * @example this.$store.commit('setCaseSearchFilter', { key: 'case_worker', val: 4 })
     * @memberof state_case
     */
    setCaseSearchFilter (state, obj) {
        Vue.set(state.filters, obj.key, obj.val)
        location.hash = `/cases?${ makeQueryString(state, false) }`
    },
    /**
     * Reset state.filters to initial values
     * @name clearCaseSearchFilters
     * @example this.$store.commit('clearCaseSearchFilters')
     * @memberof state_case
     */
    clearCaseSearchFilters (state) {
        state.filters = {
            sbsys_id: null,
            cpr_number: null,
            case_worker: null,
            team: null,
            expired: null
        }
    }
}

const actions = {
    /**
     * Get a list of cases from API. Use getCases to read the list.
     * @name fetchCases
     * @param {object} queryObj OPTIONAL An object containing keys and values for a query string. 
     * @example this.$store.dispatch('fetchCases') or this.$store.dispatch('fetchCases', { queryKey: 'queryValue'})
     * @memberof state_case
     */
    fetchCases: function({commit, state}, queryObj) {
        let q = ''
        if (queryObj) { // TODO: Check if we still need this
            for (let param in queryObj) {
                if (queryObj[param] !== null) {
                    q = q + `${ param }=${ queryObj[param] }&`
                }
            }
        } else {
            q = makeQueryString(state, true)
        }

        axios.get(`/cases/?${ q }`)
        .then(res => {
            commit('setCases', res.data)
        })
        .catch(err => console.log(err))
    },
    /**
     * Get a single case from API. Use getCase to read the list.
     * @name fetchCase
     * @param {number} cas_id Case ID
     * @returns {void} Use store.getter.getCase to read the info.
     * @example this.$store.dispatch('fetchCase', 42)
     * @memberof state_case
     */
    fetchCase: function({commit}, cas_id) {
        axios.get(`/cases/${ cas_id }/`)
        .then(res => {
            commit('setCase', res.data)
        })
        .catch(err => console.log(err))
    },
    /**
     * Clears the case search filters and fetches a new list of cases
     * @name resetCaseSearchFilters
     * @example this.$store.dispatch('resetCaseSearchFilters')
     * @memberof state_case
     */
    resetCaseSearchFilters: function({commit, dispatch}) {
        commit('clearCaseSearchFilters')
        dispatch('fetchCases')
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}