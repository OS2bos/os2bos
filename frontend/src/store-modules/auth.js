import axios from '../components/http/Http.js'
import router from '../router.js'
import notify from '../components/notifications/Notify.js'


const state = {
    accesstoken: null,
    refreshtoken: null,
    user: null
}

const getters = {
    getAuth (state) {
        return state.accesstoken ? true : false
    },
    getUser (state) {
        return state.user ? state.user : false
    }
}

const mutations = {
    setAccessToken (state, token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${ token }`
        sessionStorage.setItem('accesstoken', token)
        state.accesstoken = token
    },
    setRefreshToken (state, token) {
        sessionStorage.setItem('refreshtoken', token)
        state.refreshtoken = token
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
            commit('setAccessToken', res.data.access)
            commit('setRefreshToken', res.data.refresh)
            
            dispatch('setTimer')
            dispatch('fetchLists')
            router.push('/')
            notify('Du er logget ind', 'success')
        })
        .catch(err => {
            notify('Log ind fejlede', 'error', err)
            dispatch('clearAuth')
        })
    },
    setTimer: function({dispatch}) {
        setTimeout(() => {
            dispatch('refreshToken')
        }, 25000);
    },
    refreshToken: function({commit, dispatch, state}) {
        console.log('trying to refresh ', state.refreshtoken)
        if (state.refreshtoken) {
            console.log('got refreshtoken ', state.refreshtoken)
            axios.post('/token/refresh/', {
                refresh: state.refreshtoken
            })
            .then(res => {
                commit('setAccessToken', res.data.access)
                dispatch('fetchLists')
                dispatch('setTimer')
            })
            .catch(err => {
                notify('Refresh login fejlede', 'error', err)
                dispatch('clearAuth')
            })
        }
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
    autoLogin: function({commit, dispatch}) {
        // check for tokens in session storage and refresh session
        let refreshtoken = sessionStorage.getItem('refreshtoken')
        if (refreshtoken === 'null') {
            refreshtoken = null // null should not be a string
        }
        console.log('trying to autologin ', refreshtoken)
        if (refreshtoken) {
            commit('setRefreshToken', refreshtoken)
            dispatch('refreshToken')
        } else {
            dispatch('clearAuth')
        }
    },
    logout: function({dispatch}) {
        dispatch('clearAuth')
        notify('Du er logget ud')
    },
    clearAuth: function ({commit}) {
        commit('setAccessToken', null)
        commit('setRefreshToken', null)
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