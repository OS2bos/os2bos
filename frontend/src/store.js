/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import Vue from 'vue'
import Vuex from 'vuex'
import auth from './store-modules/auth.js'
import user from './store-modules/user.js'
import nav from './store-modules/nav.js'
import lists from './store-modules/lists.js'
import activity from './store-modules/activity.js'
import payment from './store-modules/payment.js'
import paymentsearch from './store-modules/paymentsearch.js'
import appropriation from './store-modules/appropriation.js'
import cases from './store-modules/case.js'
import error from './store-modules/error.js'
import actliststore from './components/activities/activitylist/act-list-store.js'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        auth,
        user,
        nav,
        lists,
        activity,
        payment,
        paymentsearch,
        appropriation,
        cases,
        error,
        actliststore
    }
})
