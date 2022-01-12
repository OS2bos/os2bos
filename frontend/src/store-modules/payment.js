/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import Vue from 'vue'
import notify from '../components/notifications/Notify.js'

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
    clearPaymentPlan (state) {
        state.payment_plan = {
            payment_type: 'RUNNING_PAYMENT',
            payment_frequency: 'MONTHLY',
            payment_cost_type: 'FIXED', // FIXED, GLOBAL_RATE, or PER_UNIT
            payment_amount: 0
        }
    },
    setPayment (state, payment_data) {
        const idx = state.payments.findIndex(p => p.id === payment_data.id)
        if (idx >= 0) {
            Vue.set(state.payments, idx, payment_data)
        }
    },
    setPayments (state, payments) {
        state.payments = payments
    },
    addPayments (state, payments) {
        state.payments = state.payments.concat(payments)
    },
    clearPayments (state) {
        state.payments = null
    },
    setPaymentInPayments (state, new_payment) {
        for (let p in state.payments) {
            if (state.payments[p].id === new_payment.id) {
                Vue.set(state.payments, p, new_payment)
                break
            }
        }
    },
    setPaymentsMeta (state, payments_meta) {
        state.payments_meta = payments_meta
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
    updatePayment: function({commit, dispatch}, updated_payment) {
        return axios.patch(`/payments/${ updated_payment.id }/`, updated_payment)
        .then(res => {
            notify('Betaling opdateret', 'success')
            commit('setPayment', res.data)
        })
        .catch(err => dispatch('parseErrorOutput', err))
    },
    fetchPayments: function({commit}, payload) {
        /* 
            `payload` assumes {
                payment_schedule_pk
                year (optional)
                endCursor (optional)
            }
        */
        const payment_schedule_id = btoa('PaymentSchedule:' + payload.payment_schedule_pk)
        let qry_args = `paymentSchedule:"${ payment_schedule_id }" first:30`
        if (payload.endCursor) {
            qry_args += ` after:"${ payload.endCursor }"`
        }
        if (payload.year) {
            qry_args += ` date_Gte:"${ payload.year }-01-01" date_Lte:"${ payload.year }-12-31"`
        }
        const qry = {
            query: `{
                payments(${qry_args}) {
                    totalCount,
                    pageInfo {
                        hasNextPage,
                        hasPreviousPage,
                        startCursor,
                        endCursor
                    }
                    edges {
                        cursor,
                        node {
                            pk,
                            amount,
                            date,
                            paidAmount,
                            paidDate,
                            note,
                            isPayableManually,
                            accountString,
                            accountAlias
                        }
                    }
                }
                paymentSchedule(id:"${ payment_schedule_id }") {
                    pk,
                    paymentId,
                    paymentMethod,
                    activity {
                        status
                    }
                }
            }`
        }
        axios.post('/graphql/', qry)
        .then(res => {
            const payments = res.data.data.payments.edges.map(p => {
                return {
                    id: p.node.pk,
                    amount: p.node.amount,
                    date: p.node.date,
                    paid: p.node.paid,
                    paid_date: p.node.paidDate,
                    paid_amount: p.node.paidAmount,
                    note: p.node.note,
                    payment_schedule__pk: res.data.data.paymentSchedule.pk,
                    payment_schedule__payment_id: res.data.data.paymentSchedule.paymentId,
                    activity__status: res.data.data.paymentSchedule.activity.status,
                    is_payable_manually: p.node.isPayableManually,
                    payment_method: res.data.data.paymentSchedule.paymentMethod,
                    account_string: p.node.accountString,
                    account_alias: p.node.accountAlias
                }
            })
            if (payload.endCursor) {
                commit('addPayments', payments)
            } else {
                commit('setPayments', payments)
            }
            let payments_meta = res.data.data.payments.pageInfo
            payments_meta.count = res.data.data.payments.totalCount
            commit('setPaymentsMeta', payments_meta)
        }) 
        .catch(err => console.error(err))
    },
    fetchPayment: function({commit}, payment_id) {
        axios.get(`/payments/${ payment_id }/`)
        .then(res => {
            commit('setPayment', res.data)
        })
        .catch(err => console.error(err))
    },
    fetchPaymentPlan: function({commit}, payment_plan_id) {
        axios.get(`/payment_schedules/${ payment_plan_id }/`)
        .then(res => {
            commit('setPaymentPlan', res.data)
            commit('setPayments', res.data.payments)
        })
        .catch(err => console.error(err))
    },
    fetchInternalPaymentRecipients: function({commit}) {
        axios.get(`/internal_payment_recipients/`)
        .then(res => {
            commit('setInternalPaymentRecipients', res.data)
        })
        .catch(err => console.error(err))
    },
    fetchRates: function({commit}) {
        axios.get(`/rates/`)
        .then(res => {
            commit('setRates', res.data)
        })
        .catch(err => console.error(err))
    },
    fetchPaymentEditablePastFlag: function({commit}) {
        axios.get('/editing_past_payments_allowed/')
        .then(res => {
            commit('setPaymentEditablePastFlag', res.data)
        })
        .catch(err => console.error(err))
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}