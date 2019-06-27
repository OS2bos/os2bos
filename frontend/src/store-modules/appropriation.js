import axios from '../components/http/Http.js'

const state = {
    appropriation: null
}

const getters = {
    getAppropriation (state) {
        return state.appropriation ? state.appropriation : false
    }
}

const mutations = {
    setAppropriation (state, appropriation) {
        state.appropriation = appropriation
    }
}

const actions = {
    fetchAppropriation: function({commit,dispatch}, appr_id) {
        axios.get(`/appropriations/${ appr_id }/`)
        .then(res => {
            dispatch('fetchCase', res.data.case)
            commit('setAppropriation', res.data)
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