/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import notify from '../components/notifications/Notify.js'


const state = {
    accesstoken: null,
    uid: null
}

const getters = {
    getAuth (state) {
        if (state.accesstoken && state.uid) {
            return {
                token: state.accesstoken,
                uid: state.uid
            }
        } else {
            return false
        }
    }
}

const mutations = {
    setAccessToken (state, token) {
        state.accesstoken = token
    },
    setUID (state, uid) {
        state.uid = uid
    }
}

const actions = {
    registerAuth: function({commit, dispatch, rootState}, authdata) {

        // First check if we can access API at all.
        axios.defaults.headers.common['Authentication'] = `Token ${ authdata.token }`
        axios.get('/users/?is_active=true')
        .then(res => {

            // Why not use the users data now that we have it
            let users = res.data
            users.map(user => {
                user.fullname = `${ user.first_name } ${ user.last_name } (${ user.username })`
            })
            commit('setUsers', users)

            // Set up auth data
            commit('setAccessToken', authdata.token)
            commit('setUID', authdata.uid)

            // Set up user
            let user = rootState.user.users.find(function(u) {
                return u.id === parseInt(authdata.uid)
            })
            commit('setUser', user)

            // Fetch remaining info
            dispatch('fetchConfig')
            dispatch('fetchLists')

        })
        .catch(err => {
            notify('Adgang nægtet', 'error')
        })
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}