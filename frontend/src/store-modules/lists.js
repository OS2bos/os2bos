import axios from '../components/http/Http.js'

const state = {
    municipalities: null,
    districts: null,
    activities: null
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
        axios.get('/activity_catalogs/')
        .then(res => {
            commit('setAct', res.data)
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