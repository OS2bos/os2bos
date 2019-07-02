import axios from '../components/http/Http.js'

const state = {
    municipalities: null,
    districts: null,
    activities: null,
    sections: null,
    users: null,
    approval_levels: null
}

const getters = {
    getMunis (state) {
        return state.municipalities ? state.municipalities : false
    },
    getDistricts (state) {
        return state.districts ? state.districts : false
    },
    getActivities (state) {
        return state.activities ? state.activities : false
    },
    getSections (state) {
        return state.sections ? state.sections : false
    },
    getUsers (state) {
        return state.users ? state.users : false
    },
    getApprovals (state) {
        return state.approval_levels ? state.approval_levels : false
    }
}

const mutations = {
    setMunis (state, munis) {
        state.municipalities = munis
    },
    setDist (state, districts) {
        state.districts = districts
    },
    setAct (state, activities) {
        state.activities = activities
    },
    setSections (state, sections) {
        state.sections = sections
    },
    setUsers (state, users) {
        state.users = users
    },
    setAppro (state, approvals) {
        state.approval_levels = approvals
    }
}

const actions = {
    fetchMunis: function({commit}) {
        axios.get('/municipalities/')
        .then(res => {
            commit('setMunis', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchDistricts: function({commit}) {
        axios.get('/school_districts/')
        .then(res => {
            commit('setDist', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchActivities: function({commit}) {
        axios.get('/activity_details/')
        .then(res => {
            commit('setAct', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchSections: function({commit}) {
        axios.get('/sections/')
        .then(res => {
            commit('setSections', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchUsers: function({commit}) {
        axios.get('/users/')
        .then(res => {
            commit('setUsers', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchApprovals: function({commit}) {
        axios.get('/approval_levels/')
        .then(res => {
            commit('setAppro', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchLists: function({dispatch}) {
        dispatch('fetchMunis')
        dispatch('fetchDistricts')
        dispatch('fetchActivities')
        dispatch('fetchSections')
        dispatch('fetchUsers')
        dispatch('fetchApprovals')
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}