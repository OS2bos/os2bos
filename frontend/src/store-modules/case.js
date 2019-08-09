/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    main_case: null
}

const getters = {
    getCase (state) {
        return state.main_case ? state.main_case : false
    }
}

const mutations = {
    setCase (state, main_case) {
        state.main_case = main_case
    }
}

const actions = {
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