/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'

const state = {
    users: null,
    user: null,
    teams: null,
    team: null
}

const getters = {
    getUsers (state) {
        return state.users ? state.users : false
    },
    getUser (state) {
        return state.user ? state.user : false
    },
    getTeams (state) {
        return state.teams ? state.teams : false
    },
    getTeam (state) {
        return state.team ? state.team : false
    }
}

const mutations = {
    setUsers (state, users) {
        state.users = users
    },
    setUser (state, user) {
        state.user = user
    },
    setTeams (state, teams) {
        state.teams = teams
    },
    setTeam (state, team) {
        state.team = team
    }
}

const actions = {
    fetchUsers: function({commit}) {
        return axios.get('/users/')
        .then(res => {
            let users = res.data
            users.map(user => {
                user.fullname = `${ user.first_name } ${ user.last_name } (${ user.username })`
            })
            commit('setUsers', users)
        })
        .catch(err => {
            console.log(err)
        })
    },
    fetchUser: async function({commit, dispatch}, user_id) {
        if (state.users) {
            let user = state.users.find(function(u) {
                return u.id === user_id
            })
            dispatch('fetchTeams')
            .then(() => {
                user.team_data = dispatch('fetchTeam', user.team)
                commit('setUser', user)
            })
        } else {
            setTimeout(() => {
                dispatch('fetchUser', user_id)
            }, 500)
        }
    },
    fetchTeams: function({commit}) {
        return axios.get('/teams/')
        .then(res => {
            commit('setTeams', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchTeam: function({commit, dispatch}, team_id) {
        function getTeam() {
            let team = state.teams.find(function(t) {
                return t.id === team_id
            })
            commit('setTeam', team)
        }
        if (state.teams) {
            getTeam()
        } else {
            dispatch('fetchTeams')
            .then(() => {
                getTeam()
            })
        }
    }

}

export default {
    state,
    getters,
    mutations,
    actions
}