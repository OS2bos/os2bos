import axios from '../components/http/Http.js'

const state = {
    activity: null,
    activity_list: null,
    activity_detail: null,
    activity_details: null
}

const getters = {
    getActivities (state) {
        return state.activity_list ? state.activity_list : false
    },
    getActivity (state) {
        return state.activity ? state.activity : false
    },
    getActivityDetails ( state ) {
        return state.activity_details ? state.activity_details : false
    },
    getActivityDetail (state) {
        return state.activity_detail ? state.activity_detail : false
    }
}

const mutations = {
    setActivityList (state, activities) {
        state.activity_list = activities
    },
    setActivity (state, activity) {
        state.activity = activity
    },
    setActDetails (state, act_details) {
        state.activity_details = act_details
    },
    setActDetail (state, act_detail) {
        state.activity_detail = act_detail
    }
}

const actions = {
    fetchActivities: function({commit}, appropriation_id) {

        function sortActs(act_list) {
            
            let list = act_list.sort(function(a,b) {
                if (a.activity_type === 'MAIN_ACTIVITY') {
                    return -1
                } else if (a.activity_type === 'SUPPL_ACTIVITY') {
                    return 1
                } else {
                    return 0
                }
            })

            let modifier_list = []
            
            for (let l in list) {
                const l_item = list[l]
                if (l_item.modifies) {
                    modifier_list.push(l_item)
                    const modifier = list.splice(l, 1)
                }
            }
            for (let m of modifier_list) {
                const modified_idx = list.findIndex(function(e) {
                    return e.id === m.modifies
                })
                list.splice(modified_idx + 1, 0, m)
            }

            return list
        }

        if (appropriation_id) {
            return axios.get(`/activities/?appropriation=${ appropriation_id }`)
            .then(res => {
                commit('setActivityList', sortActs(res.data))
            })
            .catch(err => console.log(err))
        } else {
            return axios.get(`/activities/`)
            .then(res => {
                commit('setActivityList', sortActs(res.data))
            })
            .catch(err => console.log(err))
        }
    },
    fetchActivity: function({commit, dispatch}, act_id) {
        axios.get(`/activities/${ act_id }/`)
        .then(res => {
            dispatch('fetchPaymentSchedule', res.data.payment_plan)
            dispatch('fetchAppropriation', res.data.appropriation)
            commit('setActivity', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchActivityDetails: function({commit}) {
        return axios.get('/activity_details/')
        .then(res => {
            commit('setActDetails', res.data)
        })
        .catch(err => console.log(err))
    },
    fetchActivityDetail: function({commit}, act_detail_id) {
        axios.get(`/activity_details/${ act_detail_id }/`)
        .then(res => {
            commit('setActDetails', res.data)
        })
        .catch(err => console.log(err))
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}