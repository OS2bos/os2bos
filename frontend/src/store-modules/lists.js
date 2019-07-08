import axios from '../components/http/Http.js'

const state = {
    municipalities: null,
    districts: null,
    sections: null,
    approval_levels: null,
    activity_details: null
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
    getActivityDetails ( state ) {
        return state.activity_details ? state.activity_details : false
    }
}

const mutations = {
    setMunis (state, munis) {
        state.municipalities = munis
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
    setActDetails (state, act_details) {
        state.activity_details = act_details
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
    fetchActivityDetails: function({commit}) {
        return axios.get('/activity_details/')
        .then(res => {
            commit('setActDetails', res.data)
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
    fetchLists: function({dispatch}) {
        return Promise.all([
            dispatch('fetchUsers'),
            dispatch('fetchTeams'),
            dispatch('fetchMunis'),
            dispatch('fetchDistricts'),
            dispatch('fetchActivityDetails'),
            dispatch('fetchSections'),
            dispatch('fetchApprovals')
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