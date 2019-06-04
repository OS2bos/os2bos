import Vue from 'vue'
import Vuex from 'vuex'
import auth from './store-modules/auth.js'
import nav from './store-modules/nav.js'
import lists from './store-modules/lists.js'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        auth: auth,
        nav: nav,
        lists: lists
    },
    state: {

    },
    mutations: {

    },
    actions: {

    }
})
