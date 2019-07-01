import axios from '../components/http/Http.js'

const state = {
    payment_schedule: null
}

const getters = {
    getPaymentSchedule (state) {
        return state.payment_schedule ? state.payment_schedule : false
    }
}

const mutations = {
    setPaymentSchedule (state, payment_schedule) {
        state.payment_schedule = payment_schedule
    }
}

const actions = {
    fetchPaymentSchedule: function({commit}, payment_id) {
        axios.get(`/payment_schedules/${ payment_id }/`)
        .then(res => {
            commit('setPaymentSchedule', res.data)
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