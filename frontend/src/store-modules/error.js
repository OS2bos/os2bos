/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import notify from '../components/notifications/Notify.js'

const state = {
    errors: null
}

const getters = {
    getErrors (state) {
        return state.errors
    }
}

const mutations = {
    addError (state, err_obj) {
        if (state.errors === null) {
            state.errors = {}
        } 
        state.errors[err_obj.err_key] = err_obj.err_msgs
    },
    clearErrors (state) {
        state.errors = null
    }
}

const actions = {
    parseErrorOutput: function({ commit }, err) {
        if (err.response) {

            function checkForArray(err_obj) {
                if (Array.isArray(err_obj)) {
                    return true
                }
            }

            function checkForString(err_obj) {
                if (typeof err_obj === 'string') {
                    return true
                }
            }

            function cycleErrKeys(err_obj) {
                for (let err in err_obj) {
                    if (checkForString(err_obj[err])) {
                        notify(err_obj[err], 'error')
                    } else if (checkForArray(err_obj[err])) {
                        commit('addError', {
                            err_key: err,
                            err_msgs: err_obj[err]
                        })
                        for (let e in err_obj[err]) {
                            notify(err_obj[err][e], 'error')
                        }
                    } else {
                        cycleErrKeys(err_obj[err])
                    }
                }
            }
            
            if (typeof(err.response.data) === 'object') {
                cycleErrKeys(err.response.data)
            } else {
                notify(err.response.data, 'error')
            }

        } else if (err.request) {
            notify(err.request.responseText, 'error')
        } else if (err.message) {
            notify(err.message, 'error')
        } else {
            notify('Der skete en ukendt fejl', 'error')
        }
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}