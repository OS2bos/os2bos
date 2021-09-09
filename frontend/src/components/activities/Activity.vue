<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section v-if="act" class="activity">
        <header class="activity-header">
            <h1>
                <i class="material-icons">style</i>
                Udgift til <span v-if="act.details_data">{{ act.details_data.name }}</span>
                <span v-if="payment_plan.fictive" class="dim">(Fiktiv)</span>
            </h1>
            <template v-if="user_can_edit === true && !edit_mode">
                <router-link v-if="can_adjust" class="btn act-edit-btn" style="margin-left: 1rem;" :to="`/activity/create?mode=expected`">+ Lav forventet justering</router-link>
                <button v-if="act.status !== 'GRANTED'" class="act-edit-btn" @click="edit_mode = true" style="margin-left: 1rem;">Redigér</button>
                <button v-if="act.status !== 'GRANTED'" class="act-delete-btn" @click="preDeleteCheck()">Slet</button>
            </template>
        </header>

        <div :class="`act-edit-header activity-${ act.status }`" v-if="!edit_mode">
            <dl>
                <dt>Foranstaltningssag</dt>
                <dd>{{ appropriation.sbsys_id }}</dd>
            </dl>
            <dl>
                <dt>SBSYS-hovedsag</dt>
                <dd>{{ cas.sbsys_id }}</dd>
            </dl>
            <dl>
                <dt>Sagspart (CPR, navn)</dt>
                <dd>
                    {{ cas.cpr_number }}, {{ cas.name }}
                </dd>
            </dl>
            <dl>
                <dt>Bevilges efter §</dt>
                <dd v-if="appropriation">{{ displaySection(appropriation.section) }}</dd>
            </dl>
        </div>

        <activity-edit v-if="edit_mode" @save="update" @cancel="update" :class="`activity-${ act.status }`" />
        
        <activity-summary v-else :activity-data="act" :class="`activity-${ act.status }`" />

        <!-- Delete activity modal -->
        <div v-if="showModal">
            <form @submit.prevent="deleteActivity()" class="modal-form">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div class="modal-container">

                            <div class="modal-header">
                                <slot name="header">
                                    <h2>Slet</h2>
                                </slot>
                            </div>

                            <div class="modal-body">
                                <slot name="body">
                                    <p>
                                        Er du sikker på, at du vil slette denne
                                        <span v-if="act.status === 'DRAFT'">kladde</span>
                                        <span v-if="act.status === 'EXPECTED'">forventning</span> ?
                                    </p>
                                </slot>
                            </div>

                            <div class="modal-footer">
                                <slot name="footer">
                                    <button type="button" class="modal-cancel-btn" @click="update">Annullér</button>
                                    <button class="modal-delete-btn" type="submit">Slet</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
        
        <payment-schedule :p-id="payment_plan.payment_id" :edit_mode="edit_mode"/>
        
    </section>

</template>

<script>
import ActDisplayMixin from '../mixins/ActivityDisplayMixin.js'
import ActivityEdit from './ActivityEdit.vue'
import ActivitySummary from './ActivitySummary.vue'
import axios from '../http/Http.js'
import PaymentSchedule from '../payments/PaymentList.vue'
import { sectionId2name } from '../filters/Labels.js'
import notify from '../notifications/Notify.js'
import PermissionLogic from '../mixins/PermissionLogic.js'

export default {

    mixins: [
        ActDisplayMixin,
        PermissionLogic
    ],
    components: {
        PaymentSchedule,
        ActivityEdit,
        ActivitySummary
    },
    data: function() {
        return {
            edit_mode: false,
            showModal: false
        }
    },
    computed: {
        cas: function() {
            return this.$store.getters.getCase
        },
        can_adjust: function() {
            // Adjust only if parent activity was granted and has no other modifying activities
            if (this.appropriation && this.act.status === 'GRANTED') {
                console.log('got appro',this.appropriation)
                let modifier = this.appropriation.activities.filter(ac => {
                    return ac.modifies === this.act.id
                })
                if (modifier.length < 1) {
                    return true
                } else {
                    return false
                }
            } else {
                return false
            }
        }
    },
    methods: {
        updateBreadCrumb: function(cas, appropriation, activity) {
            this.$store.commit('setBreadcrumb', [
                {
                    link: '/',
                    title: 'Sager'
                },
                {
                    link: `/case/${ cas.id }`,
                    title: `Hovedsag ${ cas.sbsys_id }, ${ cas.name }`
                },
                {
                    link: `/appropriation/${ appropriation.id }`,
                    title: `Bevillingsskrivelse ${ appropriation.sbsys_id }`
                },
                {
                    link: false,
                    title: `Udgift til ${ activity.details_data.name }`
                }
            ])
        },
        update: function(activity_id) {
            this.edit_mode = false
            this.showModal = false
            this.fetchActivity(activity_id)
        },
        fetchActivity: function(act_id) {
            if (act_id) {
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
                                paymentAmount
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
                                            pk
                                        }
                                    }
                                }
                            }
                        }
                    }`
                }
                axios.post('/graphql/', data)
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
                                modifies: e.node.modifies ? e.node.modifies.pk : null
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
                        payment_units: a.paymentPlan.paymentUnits,
                        payment_amount: a.paymentPlan.paymentAmount
                    }
                    this.$store.commit('setCase', new_case)
                    this.$store.commit('setAppropriation', new_appropriation)
                    this.$store.commit('setActivity', new_activity)
                    this.$store.commit('setPaymentPlan', new_payment_plan)

                    this.updateBreadCrumb(new_case, new_appropriation, new_activity)
                }) 
            }
        },
        displaySection: function(id) {
            return sectionId2name(id)
        },
        preDeleteCheck: function() {
            this.showModal = true
        },
        deleteActivity: function() {
            axios.delete(`/activities/${ this.act.id }/`)
            .then(() => {
                this.$router.push(`/appropriation/${ this.appropriation.id }`)
                notify('Ydelse slettet', 'success')
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        }
    },
    beforeRouteUpdate(to, from, next) {
        if (to.params.actId !== from.params.actId) {
            this.update(to.params.actId)
        }
        next()
    },
    created: function(){
        this.update(this.$route.params.actId)
    }
}
    
</script>

<style>

    .activity {
        margin: 1rem 2rem 2rem;
    }

    .activity-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .activity-header .material-icons {
        font-size: 3rem;
    }

    .activity .act-edit-btn {
        margin: 0 1rem;
    }

    .activity .act-delete-btn,
    .activity .modal-delete-btn {
        margin: 0;
        border-color: var(--danger);
        color: var(--danger);
        background-color: transparent;
    }
    .modal-delete-btn {
        float: right;
        margin-left: 0.5rem;
    }

    .activity .act-delete-btn:focus,
    .activity .act-delete-btn:hover,
    .activity .act-delete-btn:active,
    .modal-delete-btn:focus,
    .modal-delete-btn:hover,
    .modal-delete-btn:active {
        background-color: var(--danger);
        color: var(--grey0);
        border-color: var(--danger);
    }

    .act-edit-header {
        background-color: var(--grey1);
        padding: 1rem 2rem;
        display: grid;
        grid-template-columns: repeat( auto-fill, minmax(20rem, 1fr) );
        gap: 2rem;
        margin-bottom: .25rem;
    }

    .act-edit-header > dl {
        margin: 0;
        border-right: 1px solid var(--grey0);
    }

    .act-edit-header > dl > dt {
        padding-top: 0;
    }

    .activity .payment_schedule {
        margin: 0 0 1rem;
    }

    .activity-EXPECTED {
        background-color: hsl(40, 90%, 80%);
    }

</style>