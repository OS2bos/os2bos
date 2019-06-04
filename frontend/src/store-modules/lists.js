import axios from '../components/http/Http.js'

const state = {
    municipalities: null,
    districts: null,
    sections: null
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
    fetchSections: function({commit}) {
        axios.get('/sections/')
        .then(res => {
            commit('setSections', res.data)
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