import Vue from 'vue'
import Router from 'vue-router'
import Cases from './components/cases/Cases.vue'
import Case from './components/cases/Case.vue'
import CaseEdit from './components/cases/CaseEdit.vue'
import FamilyOverviewEdit from './components/familyoverview/FamilyOverviewEdit.vue'
import Assessment from './components/assessments/Assessment.vue'
import Appropriation from './components/appropriations/Appropriation.vue'
import AppropriationEdit from './components/appropriations/AppropriationEdit.vue'
import Activity from './components/activities/Activity.vue'
import ActivityEdit from './components/activities/ActivityEdit.vue'
import Login from './components/auth/Login.vue'
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
            path: '/case/:id',
            name: 'case',
            component: Case
        },
        {
            path: '/case-create/',
            name: 'case-create',
            component: CaseEdit
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
            component: ActivityEdit
        },
        {
            path: '/login',
            name: 'login',
            component: Login
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            //component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
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