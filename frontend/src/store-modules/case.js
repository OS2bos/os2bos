/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import Vue from 'vue'

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
    setCaseSearchFilter (state, obj) {
        Vue.set(state.filters, obj.key, obj.val)
    },
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
     * @param {object} queryObj an object containing keys and values for a query string
     * @returns {void} Use store.getter.getCases to read the list.
     * @example this.$store.dispatch('fetchCases', { queryKey: 'queryValue'})
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
            if (state.filters.sbsys_id) {
                q = q + `sbsys_id=${ state.filters.sbsys_id }&`
            }
            if (state.filters.cpr_number) {
                q = q + `cpr_number=${ state.filters.cpr_number }&`
            }
            if (state.filters.expired) {
                q = q + `expired=${ state.filters.expired }&`
            }
            if (state.filters.team) {
                q = q + `team=${ state.filters.team }&`
            }
            if (state.filters.case_worker) {
                q = q + `case_worker=${ state.filters.case_worker }&`
            }
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