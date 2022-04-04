/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import notify from '../components/notifications/Notify.js'

const state = {
    config: null
}

const getters = {
    getConfig (state) {
        return state.config
    }
}

const mutations = {
    setConfig (state, config) {
        state.config = config
    }
}

const actions = {
    fetchConfig: function({commit}) {

        axios.get('/frontend-settings/')
        .then(conf => {
            commit('setConfig', conf.data)
        })
        .catch(err => {
            notify('Konfiguration kunne ikke indlæses', 'error')
        })
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}