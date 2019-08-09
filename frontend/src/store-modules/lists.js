/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    municipalities: null,
    districts: null,
    sections: null,
    approval_levels: null,
    service_providers: null
}

const getters = {
    getMunis (state) {
        return state.municipalities ? state.municipalities : false
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
    }
}

const mutations = {
    setMunis (state, munis) {
        state.municipalities = munis.sort(function(a,b) {
            if (a.name > b.name) { return 1 } 
            if (a.name < b.name) { return -1 }
            return 0
        })
    },
    setDist (state, districts) {
        state.districts = districts.sort(function(a,b) {
            if (a.name > b.name) { return 1 } 
            if (a.name < b.name) { return -1 }
            return 0
        })
    },
    setSections (state, sections) {
        state.sections = sections
    },
    setAppro (state, approvals) {
        state.approval_levels = approvals
    },
    setServiceProviders (state, sp_list) {
        state.service_providers = sp_list.sort(function(a,b) {
            if (a.name > b.name) { return 1 } 
            if (a.name < b.name) { return -1 }
            return 0
        })
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
    fetchLists: function({dispatch}) {
        return Promise.all([
            dispatch('fetchUsers'),
            dispatch('fetchTeams'),
            dispatch('fetchMunis'),
            dispatch('fetchDistricts'),
            dispatch('fetchActivityDetails'),
            dispatch('fetchSections'),
            dispatch('fetchApprovals'),
            dispatch('fetchServiceProviders')
        ])
        .then(() => {
            // Nothing yet
        })
        .catch(err => {
            console.log('something went wrong')
        })
        
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}