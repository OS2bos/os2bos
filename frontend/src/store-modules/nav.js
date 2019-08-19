/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import router from '../router.js'

const state = {
    breadcrumb: []
}

const getters = {
    getBreadcrumb (state) {
        return state.breadcrumb
    }
}

const mutations = {
    setBreadcrumb (state, bc) {
        state.breadcrumb = bc
    }
}

const actions = {
    
}

export default {
    state,
    getters,
    mutations,
    actions
}