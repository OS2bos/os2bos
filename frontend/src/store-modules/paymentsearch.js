/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import Vue from 'vue'

const makeQueryString = function(state, show_sensitive_data) {
    let q = ''
    if (state.filters.payment_schedule__payment_id) {
        q = q + `payment_schedule__payment_id=${ state.filters.payment_schedule__payment_id }&`
    }
    if (show_sensitive_data && state.filters.case__cpr_number) {
        q = q + `case__cpr_number=${ state.filters.case__cpr_number }&`
    }
    if (show_sensitive_data && state.filters.recipient_id) {
        q = q + `recipient_id=${ state.filters.recipient_id }&`
    }
    if (state.filters.payment_method) {
        q = q + `payment_method=${ state.filters.payment_method }&`
    }
    if (state.filters.interval) {
        q = q + `interval=${ state.filters.interval }&`
    }
    if (state.filters.date_week) {
        q = q + `date_week=${ state.filters.date_week }&`
    }
    if (state.filters.date_month) {
        q = q + `date_month=${ state.filters.date_month }&`
    }
    if (state.filters.date_year) {
        q = q + `date_year=${ state.filters.date_year }&`
    }
    if (state.filters.date__gte) {
        q = q + `date__gte=${ state.filters.date__gte }&`
    }
    if (state.filters.date__lte) {
        q = q + `date__lte=${ state.filters.date__lte }&`
    }
    if (state.filters.paid !== null) {
        q = q + `paid=${ state.filters.paid }&`
    }
    return q
}

const state = {
    search_payments_meta: null,
    search_payments: null,
    // Search filters:
    filters: {
        payment_schedule__payment_id: null,
        case__cpr_number: null,
        recipient_id: null,
        payment_method: null,
        interval: null,
        date_week: null,
        date_month: null,
        date_year: null,
        date__gte: null,
        date__lte: null,
        paid: null
    }
}
 
const getters = {
    getSearchPayments (state) {
        return state.search_payments ? state.search_payments : false
    },
    getSearchPaymentsMeta (state) {
        return state.search_payments_meta ? state.search_payments_meta : false
    },
     /**
     * Get payment search filter value from store.
     * @name getPaymentSearchFilter
     * @param {string} filter_key A string corresponding to a property key in state.filters
     * @returns {any} Whatever is stored in state.filters[filter_key]
     * @example this.$store.getters.getPaymentSearchFilter('payment_method')
     * @memberof state_payment
     */
    getPaymentSearchFilter: (state) => (filter_key) => {
        return state.filters[filter_key]
    }
}

const mutations = {
    setSearchPayments (state, payments) {
        state.search_payments = payments
    },
    setSearchPaymentsMeta (state, meta) {
        state.search_payments_meta = meta
    },
    /**
      * Set value of a property in state.filters
      * Also updates URL to expose query string
      * @name setPaymentSearchFilter
      * @param {object} obj An object with value pairs corresponding to the property change.
      * @example this.$store.commit('setPaymentSearchFilter', {'payment_method': INVOICE})
      */
    setPaymentSearchFilter(state, obj) {
        Vue.set(state, 'filters', Object.assign({}, state.filters, obj))
        location.hash = `/payments?${ makeQueryString(state, false)}`
    },
    /**
      * Reset state.filters to initial values
      * @name clearPaymentSearchFilters
      * @example this.$store.commit('clearPaymentSearchFilters')
      */
    clearPaymentSearchFilters (state, IntervalId) {
        state.filters = {
            payment_schedule__payment_id: null,
            case__cpr_number: null,
            recipient_id: null,
            payment_method: null,
            interval: IntervalId,
            date__gte: null,
            date__lte: null,
            paid: null
        }
    }
}

const actions = {
    fetchSearchPayments: function({commit, state}) {
        let q = ''
        q = makeQueryString(state, true)

        axios.get(`/payments/?${ q }activity__status=GRANTED`)
        .then(res => {
            commit('setSearchPaymentsMeta', res.data)
            commit('setSearchPayments', res.data.results)
        })
        .catch(err => console.log(err))
    },
    fetchMoreSearchPayments: function({commit, state}) {
        axios.get(state.search_payments_meta.next)
        .then(res => {
            let data = res.data
            let results = state.search_payments
            for (let result of res.data.results) {
                results.push(result)
            }
            data.results = results
            commit('setSearchPaymentsMeta', data)
            commit('setSearchPayments', data.results)
        })
        .catch(err => console.log(err))
    },
    /**
     * Clears the payment search filters and fetches a new list of payments
     * @name resetPaymentSearchFilters
     * @example this.$store.dispatch('resetPaymentSearchFilters')
     */
    resetPaymentSearchFilters: function({commit, IntervalId}) {
        commit('clearPaymentSearchFilters', IntervalId)
        location.hash = `/payments?${ makeQueryString(state, false)}`
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}