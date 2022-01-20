/* Copyright (C) 2022 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

function getLatestExport(exports) {
    exports.sort(function(a,b) {
        if (a.to_date === null) {
            return 1
        }
        if (a.to_date > b.to_date) {
            return -1
        }
        if (a.to_date < b.to_date) {
            return 1
        }
        if (a.to_date === b.to_date) {
            if (a.from_date === null) {
                return 1
            }
            if (a.from_date > b.from_date) {
                return -1
            }
            if (a.from_date < b.from_date) {
                return 1
            }
        }
        return 0
    })
    return exports[0]
}

const state = {
    dst_export_objs: [],
    latest_dst_export: null
}

const getters = {
    getDSTexportObjects (state) {
        return state.dst_export_objs
    },
    getLatestDSTexport (state) {
        return state.latest_dst_export
    }
}

const mutations = {
    setDSTexportObjects (state, objs) {
        state.dst_export_objs = objs
    },
    setLatestDSTexport (state, obj) {
        state.latest_dst_export = obj
    }
}

const actions = {
    fetchDSTexportedObjects: function({commit}) {
        axios.get('/dst_payloads/')
        .then(res => {
            if (res.data.length > 0) {
                commit('setDSTexportObjects', res.data)
                commit('setLatestDSTexport', getLatestExport(res.data))
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