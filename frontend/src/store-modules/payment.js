/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    payment_schedule: null,
    payments: null,
    payment: null,
}

const getters = {
    getPaymentSchedule (state) {
        return state.payment_schedule ? state.payment_schedule : false
    },
    getPayments (state) {
        return state.payments ? state.payments : false
    },
    getPayment (state) {
        return state.payment ? state.payment : false
    }
}

const mutations = {
    setPaymentSchedule (state, payment_schedule) {
        state.payment_schedule = payment_schedule
    },
    setPayments (state, payments) {
        state.payments = payments
    },
    setPayment (state, payment) {
        state.payment = payment
    }
}

const actions = {
    fetchPaymentSchedule: function({commit}, payment_id) {
        axios.get(`/payment_schedules/${ payment_id }/`)
        .then(res => {
            commit('setPaymentSchedule', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchPayments: function({commit}, queryObj) {
        let q = ''
        if (queryObj) {
            for (let param in queryObj) {
                if (queryObj[param] !== null) {
                    q = q + `${ param }=${ queryObj[param] }&`
                }
            }
        }
        axios.get(`/payments/?${ q }`)
        .then(res => {
            commit('setPayments', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchPayment: function({commit}, payment_id) {
        axios.get(`/payments/${ payment_id }`)
        .then(res => {
            commit('setPayment', res.data)
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