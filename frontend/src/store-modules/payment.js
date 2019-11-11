/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import Vue from 'vue'

const state = {
    payments: null,
    payment: {
        payment_type: 'RUNNING_PAYMENT',
        payment_frequency: 'MONTHLY',
        payment_amount: 0
    },
    payment_schedule: null
}

const getters = {
    getPayment (state) {
        return state.payment
    },
    getPayments (state) {
        return state.payments ? state.payments : false
    },
    getPaymentType (state) {
        return state.payment.payment_type
    },
    getPaymentAmount (state) {
        return state.payment.payment_amount
    },
    getPaymentUnits (state) {
        return state.payment.payment_units ? state.payment.payment_units : false
    },
    getPaymentFreq (state) {
        return state.payment.payment_frequency
    },
    getPaymentDOM (state) {
        return state.payment.payment_day_of_month ? state.payment.payment_day_of_month : false
    },
    getPaymentRecipientType (state) {
        return state.payment.recipient_type ? state.payment.recipient_type : false
    },
    getPaymentRecipientId (state) {
        return state.payment.recipient_id
    },
    getPaymentRecipientName (state) {
        return state.payment.recipient_name
    },
    getPaymentMethod (state) {
        return state.payment.payment_method ? state.payment.payment_method : false
    },
    getPaymentMethodDetails (state) {
        return state.payment.payment_method_details ? state.payment.payment_method_details : false
    },
    getPaymentSchedule (state) {
        return state.payment_schedule ? state.payment_schedule : false
    }
}

const mutations = {
    setPayment (state, payment) {
        state.payment = payment
    },
    setPayments (state, payments) {
        state.payments = payments
    },
    setPaymentType (state, type) {
        Vue.set(state.payment, 'payment_type', type)
    },
    setPaymentAmount (state, amount) {
        Vue.set(state.payment, 'payment_amount', amount)
    },
    setPaymentUnits (state, units) {
        Vue.set(state.payment, 'payment_units', units)
    },
    setPaymentFreq (state, freq) {
        Vue.set(state.payment, 'payment_frequency', freq)
    },
    setPaymentDayOfMonth (state, day_of_month) {
        Vue.set(state.payment, 'payment_day_of_month', day_of_month)
    },
    setPaymentRecipientType (state, type) {
        Vue.set(state.payment, 'recipient_type', type)
    },
    setPaymentRecipientId (state, id) {
        Vue.set(state.payment, 'recipient_id', id)
    },
    setPaymentRecipientName (state, name) {
        Vue.set(state.payment, 'recipient_name', name)
    },
    setPaymentMethod (state, method) {
        Vue.set(state.payment, 'payment_method', method)
    },
    setPaymentMethodDetails (state, details) {
        Vue.set(state.payment, 'payment_method_details', details)
    },
    setPaymentSchedule (state, payment_schedule) {
        state.payment_schedule = payment_schedule
    },
    clearPayment (state) {
        state.payment =  {
            payment_type: 'RUNNING_PAYMENT',
            payment_frequency: 'MONTHLY',
            payment_amount: 0
        }
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
    fetchMorePayments: function({commit, state}) {
        axios.get(state.payments.next)
        .then(res => {
            let data = res.data
            let results = state.payments.results
            for (let result of res.data.results) {
                results.push(result)
            }
            data.results = results
            commit('setPayments', data)
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