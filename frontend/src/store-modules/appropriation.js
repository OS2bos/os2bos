/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    appropriation: null
}

const getters = {
    getAppropriation (state) {
        return state.appropriation ? state.appropriation : false
    }
}

const mutations = {
    setAppropriation (state, appropriation) {
        state.appropriation = appropriation
    }
}

const actions = {
    fetchAppropriation: function({commit,dispatch}, appr_id) {
        axios.get(`/appropriations/${ appr_id }/`)
        .then(res => {
            dispatch('fetchCase', res.data.case)
            commit('setAppropriation', res.data)
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