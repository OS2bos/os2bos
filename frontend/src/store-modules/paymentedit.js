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
    payments_edited: {}
}

const getters = {
    getEditedPayments: (state) => {
        return state.payments_edited
    },
    getEditedPayment: (state) => (id) => {
        return state.payments_edited[id] ? state.payments_edited[id] : false
    }
}

const mutations = {
    setEditedPayment(state, payload) {
        Vue.set(state.payments_edited, payload.key, Object.assign({}, state.payments_edited[payload.key], payload.prop))
    }
}

const actions = {
    saveEditedPayment: function({state, dispatch}, id) {
        let data = {
            paid_amount: state.payments_edited[id].paid_amount,
            paid_date: state.payments_edited[id].paid_date,
            note: state.payments_edited[id] ? state.payments_edited[id].note : '',
            paid: true
        }
        return axios.patch(`/payments/${ id }/`, data)
        .then(res => {
            notify('Betaling registreret', 'success')
            return res.data
        })
        .catch(err => dispatch('parseErrorOutput', err))
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}