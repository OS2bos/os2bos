import Vue from 'vue'
import Vuex from 'vuex'
import auth from './store-modules/auth.js'
import nav from './store-modules/nav.js'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        auth: auth,
        nav: nav
    },
    state: {

    },
    mutations: {

    },
    actions: {

    }
})
