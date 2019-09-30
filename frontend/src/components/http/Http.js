/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from 'axios'
import spinner from '../spinner/Spinner.js'
import notify from '../notifications/Notify.js'
import store from '../../store.js'

const ax = axios.create({
    baseURL: '/api'
})

ax.interceptors.request.use(
    function (config) {
        spinner.spinOn()
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
        spinner.spinOff()
        return res
    },
    function (err) {
        spinner.spinOff()
        if (err.response.data.code === 'token_not_valid') {
            notify('Du er automatisk blevet logget ud', 'error')
            store.dispatch('clearAuth')
        }
        return Promise.reject(err)
    }
)

export default ax