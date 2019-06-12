import axios from '../components/http/Http.js'
import router from '../router.js'
import notify from '../components/notifications/Notify.js'


const state = {
    tokens: null,
    auth_header: null,
    user: null
}

const getters = {
    getTokens (state) {
        return state.tokens
    },
    getUser (state) {
        return state.user ? state.user : false
    }
}

const mutations = {
    setTokens (state, tokens) {
        state.tokens = tokens
    },
    setUser (state, user) {
        state.user = user
    }
}

const actions = {
    login: function({commit, dispatch, state}, authData) {
        axios.post('/token/', {
            username: authData.username,
            password: authData.password
        })
        .then(res => {
            axios.defaults.headers.common['Authorization'] = `Bearer ${ res.data.access}`
            commit('setTokens', res.data)
            dispatch('fetchUser')

            dispatch('fetchMunis')
            dispatch('fetchDistricts')
            dispatch('fetchActivities')
            dispatch('fetchSections')

            router.push('/')
            notify('Du er logget ind', 'success')
        })
        .catch(err => {
            notify('Log ind fejlede', 'error', err)
        })
    },
    refreshToken: function() {
        axios.post('/token/refresh/', {
            refresh: state.tokens.refresh
        })
        .then(res => {
            commit('setTokens', res.data)
        })
        .catch(err => {
            notify('Refresh login fejlede', 'error', err)
        })
    },
    fetchUser: function({commit}) {
        axios.get('/users/')
        .then(res => {
            commit('setUser', res.data[0])
        })
        .catch(err => {
            notify('Kunne ikke hente information om dig', 'error', err)
        })
    },
    logout: function({dispatch}) {
        axios.post('/auth/logout/', data)
        .then(() => {
            dispatch('clearAuth')
            notify('Du er nu logget ud')
        })
        .catch(err => {
            //dispatch('clearAuth')
            notify('Der opstod en fejl ved logout', err)
        })

    },
    autoLogin: function({commit, dispatch}) {

        // check for session key and user id in session storage
        const authkey = sessionStorage.getItem('authkey')
        const userid = sessionStorage.getItem('userid')
        if (authkey) {
            commit('setAuthKey', authkey)
            dispatch('fetchUser', userid)
        }

    },
    clearAuth: function ({commit}) {
        commit('setUser', null)
        router.replace('/login')
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}