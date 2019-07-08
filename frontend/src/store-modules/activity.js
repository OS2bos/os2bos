import axios from '../components/http/Http.js'

const state = {
    activity: null,
    activity_list: null
}

const getters = {
    getActivities (state) {
        return state.activity_list ? state.activity_list : false
    },
    getActivity (state) {
        return state.activity ? state.activity : false
    }
}

const mutations = {
    setActivityList (state, activities) {
        state.activity_list = activities
    },
    setActivity (state, activity) {
        state.activity = activity
    }
}

const actions = {
    fetchActivities: function({commit}, appropriation_id) {
        if (appropriation_id) {
            return axios.get(`/activities/?appropriation=${ appropriation_id }`)
            .then(res => {
                commit('setActivityList', res.data)
            })
            .catch(err => console.log(err))
        } else {
            return axios.get(`/activities/`)
            .then(res => {
                commit('setActivityList', res.data)
            })
            .catch(err => console.log(err))
        }
        
    },
    fetchActivity: function({commit, dispatch}, act_id) {
        axios.get(`/activities/${ act_id }/`)
        .then(res => {
            dispatch('fetchPaymentSchedule', res.data.payment_plan)
            dispatch('fetchAppropriation', res.data.appropriation)
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