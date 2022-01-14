/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

function getLatestExport(exports) {
    exports.sort(function(a,b) {
        if (a.from_date < b.from_date && a.from_date !== null) {
            return true
        } else {
            return false
        }
    })
    return exports[0]
}

const state = {
    dst_export_objs: [],
    latest_dst_export_date: null
}

const getters = {
    getDSTexportObjects (state) {
        return state.dst_export_objs
    },
    getLatestDSTexportDate (state) {
        return state.latest_dst_export_date
    }
}

const mutations = {
    setDSTexportObjects (state, objs) {
        state.dst_export_objs = objs
    },
    setLatestDSTexportDate (state, date) {
        state.latest_dst_export_date = date
    }
}

const actions = {
    fetchDSTexportedObjects: function({commit}) {
        axios.get('/dst_payloads/')
        .then(res => {
            if (res.data.length > 0) {
                commit('setDSTexportObjects', res.data)
                commit('setLatestDSTexportDate', getLatestExport(res.data).from_date)
            }
        })
        .catch(err => console.error(err))
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}