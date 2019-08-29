/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    activity: null,
    activity_list: null,
    main_activity_list: null,
    suppl_activity_list: null,
    activity_detail: null,
    activity_details: null
}

const getters = {
    getActivities (state) {
        return state.activity_list ? state.activity_list : false
    },
    getMainActivities (state) {
        return state.main_activity_list ? state.main_activity_list : false
    },
    getSupplActivities (state) {
        return state.suppl_activity_list ? state.suppl_activity_list : false
    },
    getActivity (state) {
        return state.activity ? state.activity : false
    },
    getActivityDetails ( state ) {
        return state.activity_details ? state.activity_details : false
    },
    getActivityDetail (state) {
        return state.activity_detail ? state.activity_detail : false
    }
}

const mutations = {
    setActivityList (state, activities) {
        state.activity_list = activities
    },
    setMainActivityList (state, activities) {
        state.main_activity_list = activities
    },
    setSupplActivityList (state, activities) {
        state.suppl_activity_list = activities
    },
    setActivity (state, activity) {
        state.activity = activity
    },
    setActDetails (state, act_details) {
        state.activity_details = act_details
    },
    setActDetail (state, act_detail) {
        state.activity_detail = act_detail
    },
    clearActivity (state) {
        state.activity = null
    },
    clearActivities (state) {
        state.activity_list = null
    }
}

const actions = {
    fetchActivities: function({commit}, appropriation_id) {

        function sortActsByType(act_list) {
            let main_acts = act_list.filter(act => act.activity_type === 'MAIN_ACTIVITY'),
                sec_acts = act_list.filter(act => act.activity_type === 'SUPPL_ACTIVITY')
            commit('setMainActivityList', sortActsByModifier(main_acts))
            commit('setSupplActivityList', sortActsByModifier(sec_acts))
        }

        function sortActsByModifier(act_list) {
            let new_list = act_list.sort(function(a,b) {
                if (b.modifies === a.id) {
                    return -1
                } else if (a.modifies === null) {
                    return 0
                } else {
                    return 1
                }
            })
            return new_list
        }

        if (appropriation_id) {
            return axios.get(`/activities/?appropriation=${ appropriation_id }`)
            .then(res => {
                sortActsByType(res.data)
            })
            .catch(err => console.log(err))
        } else {
            return axios.get(`/activities/`)
            .then(res => {
                sortActsByType(res.data)
            })
            .catch(err => console.log(err))
        }
    },
    fetchActivity: function({commit, dispatch}, act_id) {
        axios.get(`/activities/${ act_id }/`)
        .then(res => {
            dispatch('fetchAppropriation', res.data.appropriation)
            commit('setActivity', res.data)
            commit('setPaymentSchedule', res.data.payment_plan)
        })
        .catch(err => console.log(err))
    },
    fetchActivityDetails: function({commit}) {
        return axios.get('/activity_details/')
        .then(res => {
            commit('setActDetails', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchActivityDetail: function({commit}, act_detail_id) {
        axios.get(`/activity_details/${ act_detail_id }/`)
        .then(res => {
            commit('setActDetails', res.data)
        })
        .catch(err => console.log(err))
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}