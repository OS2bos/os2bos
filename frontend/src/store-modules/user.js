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
        if (user === null || user === undefined) {
            sessionStorage.removeItem('userid')
        } else {
            sessionStorage.setItem('userid', user.id)
        }
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
            commit('setUsers', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchUser: async function({commit, state, dispatch}, user_id) {
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
    fetchTeams: function({commit, state}) {
        return axios.get('/teams/')
        .then(res => {
            commit('setTeams', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchTeam: function({commit}, team_id) {
        let team = state.teams.find(function(t) {
            return t.id === team_id
        })
        commit('setTeam', team)
    }

}

export default {
    state,
    getters,
    mutations,
    actions
}