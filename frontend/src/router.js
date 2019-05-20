import Vue from 'vue'
import Router from 'vue-router'
import Cases from './components/cases/Cases.vue'
import Case from './components/cases/Case.vue'
import CaseCreate from './components/cases/CaseCreate.vue'
import Assessment from './components/assessments/Assessment.vue'
import Appropriation from './components/appropriations/Appropriation.vue'
import AppropriationEdit from './components/appropriations/AppropriationEdit.vue'
import Activity from './components/activities/Activity.vue'
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
            component: CaseCreate
        },
        {
            path: '/assessment/:id',
            name: 'assessment',
            component: Assessment
        },
        {
            path: '/appropriation/:id',
            name: 'appropriation',
            component: Appropriation
        },
        {
            path: '/activity/:id',
            name: 'activity',
            component: Activity
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

router.afterEach((to, from) => {
    store.commit('setBreadcrumb', [])
})

export default router