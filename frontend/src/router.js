/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import Vue from 'vue'
import Router from 'vue-router'
import store from './store.js'

Vue.use(Router)

const router = new Router({
    routes: [
        {
            path: '/',
            name: 'my-cases',
            component: () => import(/* webpackPreload: true */ './components/cases/Cases.vue')
        },
        {
            path: '/case/:caseId',
            name: 'case',
            component: () => import(/* webpackChunkName: "case" */ './components/cases/Case.vue')
        },
        {
            path: '/case-create/',
            name: 'case-create',
            component: () => import(/* webpackChunkName: "caseedit" */ './components/cases/CaseEdit.vue')
        },
        {
            path: '/all-cases/:query',
            name: 'some-cases',
            component: () => import(/* webpackChunkName: "allcases" */ './components/cases/AllCases.vue')
        },
        {
            path: '/all-cases/',
            name: 'all-cases',
            component: () => import(/* webpackChunkName: "allcases" */ './components/cases/AllCases.vue')
        },
        {
            path: '/case/:casid/familyoverview-create/',
            name: 'familyoverview-create',
            component: () => import(/* webpackChunkName: "familyoverview" */ './components/familyoverview/FamilyOverviewEdit.vue')
        },
        {
            path: '/case/:casid/familyoverview-edit/:famid',
            name: 'familyoverview-edit',
            component: () => import(/* webpackChunkName: "familyoverview" */ './components/familyoverview/FamilyOverviewEdit.vue')
        },
        {
            path: '/assessment/:id',
            path: '/case/:id/assessment',
            name: 'assessment',
            component: () => import(/* webpackChunkName: "assessment" */ './components/assessments/Assessment.vue')
            
        },
        {
            path: '/appropriation/:apprId',
            name: 'appropriation',
            component: () => import(/* webpackChunkName: "appropriation" */ './components/appropriations/Appropriation.vue')
            
        },
        {
            path: '/case/:caseid/appropriation-create/',
            name: 'appropriation-create',
            component: () => import(/* webpackChunkName: "appropriationedit" */ './components/appropriations/AppropriationEdit.vue')
        },
        {
            path: '/activity/:actId',
            name: 'activity',
            component: () => import(/* webpackChunkName: "activity" */ './components/activities/Activity.vue')
        },
        {
            path: '/appropriation/:apprid/activity-create/',
            name: 'activity-create',
            component: () => import(/* webpackChunkName: "activityedit" */ './components/activities/ActivityEdit.vue'),
            props: { mode: 'create' }
        },
        {
            path: '/payments/',
            name: 'payments',
            component: () => import(/* webpackChunkName: "payments" */ './components/payments/PaymentSearch.vue')
        },
        {
            path: '/payment/:payId',
            name: 'payment',
            component: () => import(/* webpackChunkName: "payment" */ './components/payments/Payment.vue')
        },
        {
            // 404 page. This route must declared last
            path: '*',
            name: 'page404',
            component: () => import(/* webpackPreload: true */ './components/http/Page404.vue')
        }
    ]
})

router.beforeEach((to, from, next) => {
    if (store.getters.getAuth) {
        // If we are authenticated, just proceed
        next()
    } else if (to.query.token && to.query.uid) {
        // We have been redirected from SSO login, set login credentials
        store.dispatch('registerAuth', to.query)
        router.push('/')
    } else {
        // Try to login
        window.location = '/api/accounts/login/'
    }
})

router.afterEach((to, from) => {
    store.commit('setBreadcrumb', [])
    store.commit('clearErrors')
})

export default router
