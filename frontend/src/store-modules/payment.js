/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    payment: {
        payment_type: 'RUNNING_PAYMENT'
    },
    payment_schedule: null
}

const getters = {
    getPayment (state) {
        return state.payment
    },
    getPaymentSchedule (state) {
        return state.payment_schedule ? state.payment_schedule : false
    }
}

const mutations = {
    setPayment (state, payment) {
        state.payment = payment
    },
    setPaymentType (state, type) {
        state.payment.payment_type = type
    },
    setPaymentAmount (state, amount) {
        state.payment.payment_amount = amount
    },
    setPaymentFreq (state, freq) {
        state.payment.payment_frequency = freq
    },
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