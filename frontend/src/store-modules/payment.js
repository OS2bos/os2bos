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
    payment_plan: null,
    payment: null
}

const getters = {
    getPaymentPlan (state) {
        return state.payment_plan
    },
    getPaymentPlanProperty: (state) => (prop) => {
        if (state.payment_plan[prop]) {
            return state.payment_plan[prop]
        } else {
            return null
        }
    },
    getPayment (state) {
        return state.payment
    },
    getPayments (state) {
        return state.payments ? state.payments : false
    }
}

const mutations = {
    setPaymentPlan (state, payment_plan) {
        state.payment_plan = payment_plan
    },
    setPaymentPlanProperty (state, obj) {
        Vue.set(state.payment_plan, obj.prop, obj.val)
    },
    removePaymentPlanProperty (state, prop) {
        delete state.payment_plan[prop]
    },
    clearPaymentPlan (state) {
        state.payment_plan = {
            payment_type: 'RUNNING_PAYMENT',
            payment_frequency: 'MONTHLY',
            payment_day_of_month: 1,
            payment_cost_type: 'FIXED', // FIXED, RATE, or PER_UNIT
            payment_amount: 0
        }
    },
    setPayment (state, payment) {
        state.payment = payment
    },
    setPayments (state, payments) {
        state.payments = payments
    },
    clearPayment (state) {
        state.payment = {
            payment_type: 'RUNNING_PAYMENT',
            payment_frequency: 'MONTHLY',
            payment_day_of_month: 1,
            payment_cost_type: 'FIXED', // FIXED, RATE, or PER_UNIT
            payment_amount: 0
        }
    }
}

const actions = {
    fetchPayments: function({commit}, queryObj) {
        let q = ''
        if (queryObj) {
            for (let param in queryObj) {
                if (queryObj[param] !== null) {
                    q = q + `${ param }=${ queryObj[param] }&`
                }
            }
        }
        axios.get(`/payments/?${ q }&activity__status=GRANTED`)
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