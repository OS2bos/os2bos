import axios from '../components/http/Http.js'

const state = {
    activity: null
}

const getters = {
    getActivity (state) {
        return state.activity ? state.activity : false
    }
}

const mutations = {
    setActivity (state, activity) {
        state.activity = activity
    }
}

const actions = {
    fetchActivity: function({commit, dispatch}, act_id) {
        axios.get(`/activities/${ act_id }/`)
        .then(res => {
            dispatch('fetchPaymentSchedule', res.data.payment_plan)
            commit('setActivity', res.data)
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