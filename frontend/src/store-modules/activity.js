/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import Vue from 'vue'
import axios from '../components/http/Http.js'
import { epoch2DateStr } from '../components/filters/Date.js'

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
    },
    getActivityProperty: (state) => (prop) => {
        if (state.activity && state.activity[prop]) {
            return state.activity[prop]
        } else {
            return null
        }
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
    },
    setActivityProperty (state, obj) {
        if (state.activity === null) {
            state.activity = {}
        }
        if (obj.val === "") {
            obj.val = null
        }
        Vue.set(state.activity, obj.prop, obj.val)
    },
    removeActivityProperty (state, prop) {
        delete state.activity[prop]
    },
    clearActivity (state) {
        state.activity = null
    },
    clearActivities (state) {
        state.activity_list = null
    }
}

const actions = {
    fetchActivities: function({commit}, appropriation_id) {
        function checkActivityAge(acts) {
            let now = epoch2DateStr(new Date())
            acts.map(function(act) {
                if (act.start_date < now && act.end_date <= now) {
                    act.is_old = true
                } else {
                    act.is_old = false
                }
            })
        }
        if (appropriation_id) {
            return axios.get(`/activities/?appropriation=${ appropriation_id }`)
            .then(res => {
                checkActivityAge(res.data)
                commit('setActivityList', res.data)
            })
            .catch(err => console.log(err))
        } else {
            return axios.get(`/activities/`)
            .then(res => {
                checkActivityAge(res.data)
                commit('setActivityList', res.data)
            })
            .catch(err => console.log(err))
        }
    },
    fetchActivity: function({dispatch}, act_id) {
        const id = btoa(`Activity:${ act_id }`)
        let data = {
            query: `{
                activity(id: "${ id }") {
                    id,
                    pk,
                    status,
                    startDate,
                    endDate,
                    activityType,
                    details {
                        id,
                        name,
                        description
                    },
                    paymentPlan {
                        pk,
                        paymentId,
                        fictive,
                        paymentType,
                        paymentCostType,
                        recipientId,
                        recipientName,
                        recipientType,
                        paymentMethod,
                        paymentFrequency,
                        paymentDate,
                        paymentDayOfMonth,
                        paymentUnits,
                        paymentAmount,
                        pricePerUnit {
                            pk,
                            currentAmount
                        },
                        paymentRate {
                            pk
                        }
                    },
                    appropriation {
                        pk,
                        sbsysId,
                        section {
                            pk
                        }
                        case {
                            pk,
                            sbsysId,
                            cprNumber,
                            name
                        },
                        activities {
                            edges {
                                node {
                                    modifies {
                                        pk
                                    },
                                    pk,
                                    startDate,
                                    endDate,
                                    activityType
                                }
                            }
                        }
                    }
                }
            }`
        }
        return axios.post('/graphql/', data)
        .then(res => {
            const a = res.data.data.activity
            const new_case = {
                id: a.appropriation.case.pk,
                sbsys_id: a.appropriation.case.sbsysId,
                name: a.appropriation.case.name,
                cpr_number: a.appropriation.case.cprNumber
            }
            const new_appropriation = {
                id: a.appropriation.pk,
                sbsys_id: a.appropriation.sbsysId,
                section: a.appropriation.section.pk,
                activities: [...a.appropriation.activities.edges.map(e => {
                    return {
                        id: Number(e.node.pk),
                        modifies: e.node.modifies ? e.node.modifies.pk : null,
                        start_date: e.node.startDate,
                        end_date: e.node.endDate,
                        activity_type: e.node.activityType
                    }
                })]
            }
            const new_activity = {
                status: a.status,
                id: a.pk,
                start_date: a.startDate,
                end_date: a.endDate,
                details: Number(a.details.id),
                details_data: {
                    name: a.details.name,
                    description: a.details.description
                },
                appropriation: Number(a.appropriation.pk),
                activity_type: a.activityType
            }
            const new_payment_plan = {
                id: a.paymentPlan.pk,
                payment_id: a.paymentPlan.paymentId,
                fictive: a.paymentPlan.fictive,
                payment_type: a.paymentPlan.paymentType,
                payment_cost_type: a.paymentPlan.paymentCostType,
                recipient_id: a.paymentPlan.recipientId,
                recipient_name: a.paymentPlan.recipientName,
                recipient_type: a.paymentPlan.recipientType,
                payment_method: a.paymentPlan.paymentMethod,
                payment_frequency: a.paymentPlan.paymentFrequency,
                payment_date: a.paymentPlan.paymentDate,
                payment_day_of_month: a.paymentPlan.paymentDayOfMonth,
                payment_amount: a.paymentPlan.paymentAmount,
                payment_units: a.paymentPlan.paymentUnits,
                price_per_unit: a.paymentPlan.pricePerUnit ? {
                    current_amount: a.paymentPlan.pricePerUnit.currentAmount,
                    id: a.paymentPlan.pricePerUnit.pk
                } : null,
                payment_rate: a.paymentPlan.paymentRate ? a.paymentPlan.paymentRate.pk : null
            }
            if (new_payment_plan.price_per_unit) {
                axios.get(`/prices/${ new_payment_plan.price_per_unit.id }/`)
                .then(res => {
                    new_payment_plan.price_per_unit.rates_per_date = res.data.rates_per_date
                    dispatch('updateStore', {
                        cas: new_case,
                        appr: new_appropriation,
                        act: new_activity,
                        pp: new_payment_plan
                    })
                })
                .catch(err => {
                    console.error('Could not fetch price information', err)
                })
            } else {
                dispatch('updateStore', {
                    cas: new_case,
                    appr: new_appropriation,
                    act: new_activity,
                    pp: new_payment_plan
                })
            }
        })
    },
    updateStore: function({commit}, payload) {
        commit('setCase', payload.cas)
        commit('setAppropriation', payload.appr)
        commit('setActivity', payload.act)
        commit('setActDetail', payload.act.details_data)
        commit('setPaymentPlan', payload.pp)
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
            commit('setActDetail', res.data)
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