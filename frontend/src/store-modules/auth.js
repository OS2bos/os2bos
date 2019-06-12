import axios from '../components/http/Http.js'
import router from '../router.js'
import notify from '../components/notifications/Notify.js'

const state = {
    csrftoken: null,
    user: null
}

const getters = {
    getCsrfToken (state) {
        return state.csrftoken
    },
    getUser (state) {
        return state.user ? state.user : false
    }
}

const mutations = {
    setCsrfToken (state, csrftoken) {
        state.csrftoken = csrftoken
    },
    setUser (state, user) {
        state.user = user
    }
}

const actions = {
    login: function({commit, dispatch, state}, authData) {

        let data = new FormData()
        data.set('csrfmiddlewaretoken', state.csrftoken)
        data.set('next', '/#/')
        data.set('username', authData.username)
        data.set('password', authData.password)
        return axios({
            method: 'post',
            url: '/auth/login/',
            data: data
        })
        .then(res => {
            const new_csrf_token = document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1")
            commit('setCsrfToken', new_csrf_token)

            router.push('/')
            
            dispatch('fetchUser')
            dispatch('fetchMunis')
            dispatch('fetchDistricts')
            dispatch('fetchActivities')
            dispatch('fetchSections')
            
            notify('Du er logget ind', 'success')
        })
        .catch(err => {
            notify('Log ind fejlede', 'error', err)
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
        let data = new FormData()
        data.set('csrfmiddlewaretoken', state.csrftoken)
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