/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import { json2jsEpoch } from '../components/filters/Date.js'

const makeQueryString = function(state, show_sensitive_data) {
    let q = ''
    if (state.filters.case__sbsys_id) {
        q = q + `case__sbsys_id=${ state.filters.case__sbsys_id }&`
    }
    if (show_sensitive_data && state.filters.case__cpr_number) {
        q = q + `case__cpr_number=${ state.filters.case__cpr_number }&`
    }
    if (state.filters.case__team) {
        q = q + `case__team=${ state.filters.case__team }&`
    }
    if (state.filters.case__case_worker) {
        q = q + `case__case_worker=${ state.filters.case__case_worker }`
    }
    if (state.filters.section) {
        q = q + `section=${ state.filters.section }`
    }
    if (state.filters.main_activity__details__id) {
        q = q + `main_activity__details__id=${ state.filters.main_activity__details__id }`
    }
    return q
}

/**
 * Vuex store methods for cases
 * @name state_appropriation
 */
const state = {
    appropriations: null,
    appropriation: null,
    appr_main_activities: false, // Contains a list of main_activities and collects their start and end dates
    // Search filters:
    filters: {
        case__sbsys_id: null,
        case__cpr_number: null,
        case__team: null,
        case__case_worker: null,
        section: null,
        main_activity__details__id: null
    }
}

const getters = {
    getAppropriations (state) {
        return state.appropriations ? state.appropriations : false
    },
    getAppropriation (state) {
        return state.appropriation ? state.appropriation : false
    },
    getAppropriationMainActs (state) {
        return state.appr_main_activities ? state.appr_main_activities : false
    }
}

const mutations = {
    setAppropriations (state, appropriations) {
        state.appropriations = appropriations
    },
    setAppropriation (state, appropriation) {
        state.appropriation = appropriation
    },
    setMainActivities (state, payload) {
        state.appr_main_activities = payload
    },
    clearAppropriation (state) {
        state.appropriation = null
        state.appr_main_activities = null 
    }
}

const actions = {
    /**
     * Get a list of cases from API. Use getCases to read the list.
     * @name fetchAppropriations
     * @param {object} queryObj an object containing keys and values for a query string
     * @returns {void} Use store.getter.getAppropriations to read the list.
     * @example this.$store.dispatch('fetchAppropriations', { queryKey: 'queryValue'})
     * @memberof state_appropriation
     */
    fetchAppropriations: function({commit}, queryObj) {
        let q = ''
        if (queryObj) {
            for (let param in queryObj) {
                if (queryObj[param] !== null) {
                    q = q + `${ param }=${ queryObj[param] }&`
                }
            }
        }
        axios.get(`/appropriations/?${ q }`)
        .then(res => {
            commit('setAppropriations', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchAppropriation: function({commit,dispatch}, appr_id) {
        axios.get(`/appropriations/${ appr_id }/`)
        .then(res => {
            dispatch('fetchMainActivities', res.data.activities)
            dispatch('fetchCase', res.data.case)
            commit('setAppropriation', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchMainActivities: function({commit}, activities) {
        let super_main_act = {
            activities: [],
            start_date: null,
            end_date: null
        }
        activities.map(el => {
            if (el.activity_type === 'MAIN_ACTIVITY') {
                super_main_act.activities.push(el)
                let start = json2jsEpoch(el.start_date),
                    end = json2jsEpoch(el.end_date)
                if (!super_main_act.start_date) {
                    super_main_act.start_date = start
                } else if (start < super_main_act.start_date) {
                    super_main_act.start_date = start
                }
                if (!super_main_act.end_date) {
                    super_main_act.end_date = end
                } else if (end > super_main_act.end_date) {
                    super_main_act.end_date = end
                }
            }
        })
        if (super_main_act.activities.length > 0) {
            commit('setMainActivities', super_main_act)
        }
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}