import axios from '../components/http/Http.js'
import router from '../router.js'
import notify from '../components/notifications/Notify.js'
import store from '../store.js';


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
        if (token === null) {
            sessionStorage.removeItem('accesstoken')
        } else {
            axios.defaults.headers.common['Authorization'] = `Bearer ${ token }`
            sessionStorage.setItem('accesstoken', token)
        }
        state.accesstoken = token
    },
    setRefreshToken (state, token) {
        if (token === null) {
            sessionStorage.removeItem('refreshtoken')
        } else {
            sessionStorage.setItem('refreshtoken', token)
        }
        state.refreshtoken = token
    },
    setUser (state, user) {
        if (user === null) {
            sessionStorage.removeItem('username')
        } else {
            sessionStorage.setItem('username', user.username)
        }
        state.user = user
    }
}

const actions = {
    login: function({commit, dispatch}, authData) {
        axios.post('/token/', {
            username: authData.username,
            password: authData.password
        })
        .then(res => {
            commit('setAccessToken', res.data.access)
            commit('setRefreshToken', res.data.refresh)
            dispatch('setTimer')
            dispatch('fetchLists')
            dispatch('fetchUser', authData.username)
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
        }, 270000);
    },
    refreshToken: function({commit, dispatch, state}) {
        if (state.refreshtoken) {    
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
    fetchUser: async function({commit, rootState}, username) {
        function waitForUsers() {
            setTimeout(function() {
                if (rootState.lists.users) {
                    const stored_username = sessionStorage.getItem('username')
                    let name = ''
                    if (username) {
                        name = username
                    } else if (stored_username) {
                        name = stored_username
                    } else {
                        return false
                    }
                    const user = rootState.lists.users.find(u => {
                        return u.username === name
                    })
                    commit('setUser', user)
                } else {
                    waitForUsers()
                }
            }, 500)
        }
        waitForUsers()
    },
    autoLogin: function({commit, dispatch}) {
        // check for tokens in session storage and refresh session
        const refreshtoken = sessionStorage.getItem('refreshtoken')
        const accesstoken = sessionStorage.getItem('accesstoken')
        if (refreshtoken) {
            commit('setAccessToken', accesstoken)
            commit('setRefreshToken', refreshtoken)
            dispatch('fetchUser')
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