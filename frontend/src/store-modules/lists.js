/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import { fetchData } from '../components/webworker/Worker.js'

const state = {
    municipalities: null,
    target_group: null,
    districts: null,
    sections: null,
    approval_levels: null,
    service_providers: null,
    effort_steps: null,
    efforts: null
}

const getters = {
    getMunis (state) {
        return state.municipalities ? state.municipalities : false
    },
    getTargetGroups (state) {
        return state.target_group ? state.target_group : false
    },
    getDistricts (state) {
        return state.districts ? state.districts : false
    },
    getSections (state) {
        return state.sections ? state.sections : false
    },
    getApprovals (state) {
        return state.approval_levels ? state.approval_levels : false
    },
    getServiceProviders ( state ) {
        return state.service_providers ? state.service_providers : false
    },
    getEffortSteps ( state ) {
        return state.effort_steps ? state.effort_steps : false
    },
    getEfforts ( state ) {
        return state.efforts ? state.efforts : false
    }
}

const mutations = {
    setMunis (state, munis) {
        state.municipalities = munis
    },
    setTarget (state, target) {
        state.target_group = target
    },
    setDist (state, districts) {
        state.districts = districts
    },
    setSections (state, sections) {
        state.sections = sections
    },
    setAppro (state, approvals) {
        state.approval_levels = approvals
    },
    setServiceProviders (state, sp_list) {
        state.service_providers = sp_list
    },
    setEffortSteps (state, effort_steps) {
        state.effort_steps = effort_steps
    },
    setEfforts (state, efforts) {
        state.efforts = efforts
    }
}

const actions = {
    fetchMunis: function({commit}) {
        return axios.get('/municipalities/')
        .then(res => {
            commit('setMunis', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchTargetGroups: function({commit}) {
        return axios.get('/target_groups/')
        .then(res => {
            commit('setTarget', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchDistricts: function({commit}) {
        return axios.get('/school_districts/')
        .then(res => {
            commit('setDist', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchSections: function({commit}) {
        return axios.get('/sections/')
        .then(res => {
            commit('setSections', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchApprovals: function({commit}) {
        return axios.get('/approval_levels/')
        .then(res => {
            commit('setAppro', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchServiceProviders: function({commit}) {
        return axios.get('/service_providers/')
        .then(res => {
            commit('setServiceProviders', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchEffortSteps: function({commit}) {
        return axios.get('/effort_steps/')
        .then(res => {
            commit('setEffortSteps', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchEfforts: function({commit}) {
        return axios.get('/efforts/')
        .then(res => {
            commit('setEfforts', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchLists: function({dispatch}) {
        dispatch('fetchTeams')
        dispatch('fetchTargetGroups')
        dispatch('fetchDistricts')
        dispatch('fetchApprovals')
        dispatch('fetchEffortSteps')
        dispatch('fetchEfforts')
        fetchData()
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}