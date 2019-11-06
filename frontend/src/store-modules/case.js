/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    cases: null,
    main_case: null
}

const getters = {
    getCases (state) {
        return state.cases ? state.cases : false
    },
    getCase (state) {
        return state.main_case ? state.main_case : false
    }
}

const mutations = {
    setCases (state, cases) {
        state.cases = cases
    },
    setCase (state, main_case) {
        state.main_case = main_case
    },
    clearCase (state) {
        state.main_case = null
    }
}

const actions = {
    fetchCases: function({commit}, queryObj) {
        let q = ''
        if (queryObj) {
            for (let param in queryObj) {
                if (queryObj[param] !== null) {
                    q = q + `${ param }=${ queryObj[param] }&`
                }
            }
        }
        axios.get(`/cases/?${ q }`)
        .then(res => {
            commit('setCases', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchCase: function({commit}, cas_id) {
        axios.get(`/cases/${ cas_id }/`)
        .then(res => {
            commit('setCase', res.data)
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