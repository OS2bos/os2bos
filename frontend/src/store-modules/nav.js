import router from '../router.js'

const state = {
    breadcrumb: []
}

const getters = {
    getBreadcrumb (state) {
        return state.breadcrumb
    }
}

const mutations = {
    setBreadcrumb (state, bc) {
        state.breadcrumb = bc
    }
}

const actions = {
    
}

export default {
    state,
    getters,
    mutations,
    actions
}