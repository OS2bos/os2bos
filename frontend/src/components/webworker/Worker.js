/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import store from '../../store.js'

function fetchData() {
    if (window.Worker) {
        const myWorker = new Worker('/js/webworker.js')
        myWorker.postMessage('go')
        myWorker.addEventListener('message', function(ev) {
            store.commit('setSections', ev.data.sections)
            store.commit('setServiceProviders', ev.data.service_providers)
            store.commit('setActDetails', ev.data.activity_details)
            store.commit('setMunis', ev.data.municipalities)
        })
        myWorker.addEventListener('error', function(ev) {
            console.error(ev.message)
        })
    }
}    

export {
    fetchData
}