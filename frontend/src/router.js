/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import Vue from 'vue'
import Router from 'vue-router'
import Cases from './components/cases/Cases.vue'
import AllCases from './components/cases/AllCases.vue'
import Case from './components/cases/Case.vue'
import CaseEdit from './components/cases/CaseEdit.vue'
import FamilyOverviewEdit from './components/familyoverview/FamilyOverviewEdit.vue'
import Assessment from './components/assessments/Assessment.vue'
import Appropriation from './components/appropriations/Appropriation.vue'
import AppropriationEdit from './components/appropriations/AppropriationEdit.vue'
import Activity from './components/activities/Activity.vue'
import ActivityEdit from './components/activities/ActivityEdit.vue'
import PaymentSchedule from './components/payment/PaymentSchedule.vue'
import Login from './components/auth/Login.vue'
import Page404 from './components/http/Page404.vue'
import store from './store.js'

Vue.use(Router)

const router = new Router({
    routes: [
        {
            path: '/',
            name: 'home',
            component: Cases
        },
        {
            path: '/my-cases/',
            name: 'my-caces',
            component: Cases
        },
        {
            path: '/case/:caseId',
            name: 'case',
            component: Case
        },
        {
            path: '/case-create/',
            name: 'case-create',
            component: CaseEdit
        },
        {
            path: '/all-cases/:query',
            name: 'some-cases',
            component: AllCases
        },
        {
            path: '/all-cases/',
            name: 'all-cases',
            component: AllCases
        },
        {
            path: '/case/:casid/familyoverview-create/',
            name: 'familyoverview-create',
            component: FamilyOverviewEdit
        },
        {
            path: '/case/:casid/familyoverview-edit/:famid',
            name: 'familyoverview-edit',
            component: FamilyOverviewEdit
        },
        {
            path: '/assessment/:id',
            path: '/case/:id/assessment',
            name: 'assessment',
            component: Assessment
        },
        {
            path: '/appropriation/:id',
            name: 'appropriation',
            component: Appropriation
        },
        {
            path: '/case/:caseid/appropriation-create/',
            name: 'appropriation-create',
            component: AppropriationEdit
        },
        {
            path: '/activity/:id',
            name: 'activity',
            component: Activity
        },
        {
            path: '/appropriation/:apprid/activity-create/',
            name: 'activity-create',
            component: ActivityEdit,
            props: { mode: 'create' }
        },
        {
            path: '/paymentschedule/',
            name: 'paymentschedule',
            component: PaymentSchedule
        },
        {
            path: '/login',
            name: 'login',
            component: Login
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            //component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
        },
        {
            // This route must declared last
            path: '*',
            name: 'page404',
            component: Page404
        }
    ]
})

router.beforeEach((to, from, next) => {
    if (to.name === 'login') {
        next()
    } else if (sessionStorage.getItem('accesstoken')) {
        next()
    } else {
        next({
            path: '/login'
        }) 
    }
})

router.afterEach((to, from) => {
    store.commit('setBreadcrumb', [])
})

export default router