/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import Vue from 'vue'

const state = {
    payment_plan: null,
    payments_meta: null,
    payments: null,
    payment: null,
    internal_payment_recipients: null,
    rates: null,
    payments_are_editable_in_the_past: true // to be updated by fetchPaymentEditablePastFlag but will generally be true
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
    getPaymentsMeta (state) {
        return state.payments_meta ? state.payments_meta : false
    },
    getPayments (state) {
        return state.payments ? state.payments : false
    },
    getInternalPaymentRecipients (state) {
        return state.internal_payment_recipients ? state.internal_payment_recipients : false
    },
    getRates (state) {
        return state.rates ? state.rates : false
    },
    getPaymentEditablePastFlag (state) {
        return state.payments_are_editable_in_the_past
    }
}

const mutations = {
    setPaymentPlan (state, payment_plan) {
        state.payment_plan = payment_plan
        state.payments = payment_plan.payments
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
            payment_cost_type: 'FIXED', // FIXED, GLOBAL_RATE, or PER_UNIT
            payment_amount: 0
        }
    },
    setPayment (state, payment) {
        state.payment = payment
    },
    setPayments (state, payments) {
        state.payments = payments
    },
    setPaymentsMeta (state, payments_meta) {
        state.payments_meta = payments_meta
    },
    clearPayment (state) {
        state.payment = {
            payment_type: 'RUNNING_PAYMENT',
            payment_frequency: 'MONTHLY',
            payment_day_of_month: 1,
            payment_cost_type: 'FIXED', // FIXED, GLOBAL_RATE, or PER_UNIT
            payment_amount: 0
        }
    },
    setPaymentEditRowData (state, obj) {
        let payment_idx = state.payments.findIndex(p => {
            return p.id === obj.idx
        })
        Vue.set(state.payments[payment_idx], obj.prop, obj.val)
    },
    setInternalPaymentRecipients (state, internal_payment_recipients) {
        state.internal_payment_recipients = internal_payment_recipients
    },
    setRates (state, rates) {
        state.rates = rates
    },
    setPaymentEditablePastFlag (state, bool) {
        state.payments_are_editable_in_the_past = bool
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
            commit('setPaymentsMeta', res.data)
            commit('setPayments', res.data.results)
        })
        .catch(err => console.log(err))
    },
    fetchMorePayments: function({commit, state}) {
        axios.get(state.payments_meta.next)
        .then(res => {
            let data = res.data
            let results = state.payments
            for (let result of res.data.results) {
                results.push(result)
            }
            data.results = results
            commit('setPaymentsMeta', data)
            commit('setPayments', data.results)
        })
        .catch(err => console.log(err))
    },
    fetchPayment: function({commit}, payment_id) {
        axios.get(`/payments/${ payment_id }/`)
        .then(res => {
            commit('setPayment', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchPaymentPlan: function({commit}, payment_plan_id) {
        axios.get(`/payment_schedules/${ payment_plan_id }/`)
        .then(res => {
            commit('setPaymentPlan', res.data)
            commit('setPayments', res.data.payments)
        })
        .catch(err => console.log(err))
    },
    fetchInternalPaymentRecipients: function({commit}) {
        axios.get(`/internal_payment_recipients/`)
        .then(res => {
            commit('setInternalPaymentRecipients', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchRates: function({commit}) {
        axios.get(`/rates/`)
        .then(res => {
            commit('setRates', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchPaymentEditablePastFlag: function({commit}) {
        axios.get('/editing_past_payments_allowed/')
        .then(res => {
            commit('setPaymentEditablePastFlag', res.data)
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