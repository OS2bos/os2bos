import axios from '../components/http/Http.js'
import router from '../router.js'
import notify from '../components/notifications/Notify.js'

const state = {
    sessionKey: null,
    user: null
}

const getters = {
    isAuthenticated (state) {
        return state.sessionKey ? state.sessionKey : false
    },
    getUser (state) {
        return state.user ? state.user : false
    }
}

const mutations = {
    setAuthKey (state, sid) {
        state.sessionKey = sid
    },
    setUser (state, user) {
        state.user = user
    }
}

const actions = {
    login: function({commit, dispatch}, authData) {

        let data = new FormData()
        data.append("username", authData.username)
        data.append("password", authData.password)
        return axios({
            method: 'post',
            url: '/auth/login/',
            data: data
        })
        .then(res => {
            
            commit('setAuthKey', res.data.key)

            // Save session key and user id in session storage
            sessionStorage.setItem('authkey', res.data.key)
            sessionStorage.setItem('userid', res.data.user)
            
            dispatch('fetchUser', res.data.user)
            notify('Du er logget ind', 'success')
            return false
        })
        .catch(err => {
            if (err.response.data.password || err.response.data.username) {
                notify('Log ind fejlede', 'error')
            } else {
                notify('Log ind fejlede', 'error', err.response.data)
            }
            return err.response.data
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
    fetchUser: function({commit, state, dispatch}, user_id) {
        if (!state.sessionKey) {
            return
        }
        axios({
            method: 'get',
            url: `/auth/user/${ user_id }/`,
            headers: {
                'Authorization': 'Token ' + state.sessionKey
            }
        })
        .then(res => {
            commit('setUser', res.data)
            if (router.history.current.query.redirect) {
                router.push(router.history.current.query.redirect)
            } else {
                if (state.user.is_staff) {
                    router.push('/dashboard')
                } else {
                    router.push('/my-bookings')
                }
            }
        })
        .catch(err => {
            console.log('could not fetch user')
            dispatch('cleanPostLogout')
        })

    },
    logout: function({dispatch}) {

        axios({
            method: 'post',
            url: '/auth/logout/',
            headers: {
                'Authorization': 'Token ' + state.sessionKey
            }
        })
        .then(res => {
            dispatch('cleanPostLogout')
            notify('Du er nu logget ud')
        })
        .catch(err => {
            dispatch('cleanPostLogout')
            notify('Der opstod en fejl. Du er nu logget ud', err)
        })

    },
    clearAuth: function({commit}) {
        sessionStorage.removeItem('authkey')
        sessionStorage.removeItem('userid')
        commit('setAuthKey', null)
        commit('setUser', null)
    },
    cleanPostLogout: function ({dispatch}) {
        dispatch('clearAuth')
        router.replace('/login')
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}