/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from 'axios'
import spinner from '../spinner/Spinner.js'
import notify from '../notifications/Notify.js'

const ax = axios.create({
    baseURL: '/api'
})

let load_stack = []

function checkSpin() {
    if (load_stack.length > 0) {
        spinner.spinOn()
    } else {
        spinner.spinOff()
    }
}

ax.interceptors.request.use(
    function (config) {
        load_stack.push(true)
        checkSpin()
        return config
    },
    function (err) {
        if (!error.status) {
            // network error
            notify('Der er et problem med netværket', 'error')
        }
        return Promise.reject(err)
    }
)

ax.interceptors.response.use(
    function (res) {
        load_stack.pop()
        checkSpin()
        return res
    },
    function (err) {
        load_stack.pop()
        checkSpin()
        return Promise.reject(err)
    }
)

export default ax