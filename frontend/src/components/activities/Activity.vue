<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section class="activity" v-if="act && act.id">
        <header class="activity-header">
            <h1>
                <i class="material-icons">style</i>
                Udgift til <span v-html="actId2name(act.details)"></span>
                <span v-if="act.payment_plan.fictive" class="dim">(Fiktiv)</span>
            </h1>
            <template v-if="permissionCheck === true">
                <router-link v-if="can_adjust" class="btn act-edit-btn" style="margin-left: 1rem;" :to="`/activity/create?mode=expected`">+ Lav forventet justering</router-link>
                <button v-if="act.status !== 'GRANTED'" class="act-delete-btn" @click="preDeleteCheck()" style="margin-left: 1rem;">Slet</button>
            </template>
        </header>

        <div :class="`act-edit-header activity-${ act.status }`">
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

        <form @submit.prevent="saveChanges" :class="`act-edit-form activity-${ act.status }`">
            <div class="act-edit-main">

                <div>
                    <dl v-if="act.status === 'GRANTED'">
                        <dt>
                            Godkendt af
                        </dt>
                        <dd>
                            <p>
                                <em>{{ displayUserName(act.approval_user) }}</em> d. {{ displayDate(act.appropriation_date) }}<br>
                                ({{ displayApprLevel(act.approval_level) }} kompetence)
                            </p>
                            <p v-if="act.approval_note">Note: {{ act.approval_note }}</p>
                        </dd>
                    </dl>
                    <activity :editable="false" />
                    <type />
                    <status :editable="is_editable" />
                    <fictional :editable="is_editable" />
                </div>
                
                <div>
                    <payment-type :editable="false" />
                    <template v-if="payment_plan.payment_type === 'ONE_TIME_PAYMENT'">
                        <pay-date-single :editable="is_editable" />
                    </template>
                    <div v-if="payment_plan.payment_type === 'RUNNING_PAYMENT'">
                        <pay-date-start :editable="is_editable" />
                        <pay-date-end :editable="is_editable" />
                        <payment-frequency :editable="is_editable" />
                    </div>
                </div>

                <div>
                    <cost-type :editable="false" />
                    <cost-type-fixed :editable="is_editable" /> <!-- TODO: REMOVE WHEN API IS WORKING -->
                    <template v-if="payment_plan.payment_cost_type === 'FIXED'">
                        <cost-type-fixed :editable="is_editable" />
                    </template>
                    <template v-if="payment_plan.payment_cost_type === 'RATE'">
                        <cost-type-rate :editable="is_editable" />
                    </template>
                    <template v-if="payment_plan.payment_cost_type === 'PER_UNIT'">
                        <cost-type-per-unit :editable="is_editable" />
                    </template>
                    <template v-if="payment_plan.payment_cost_type === 'PER_UNIT' || payment_plan.payment_cost_type === 'RATE'">
                        <pay-plan-calc />
                    </template>
                </div>

                <div>
                    <payment-receiver-type :editable="is_editable" />

                    <template v-if="payment_plan.recipient_type === 'INTERNAL'" >
                        <payment-internal-receiver :editable="is_editable" /> 
                        <payment-receiver-id :editable="is_editable" />
                    </template>

                    <template v-if="payment_plan.recipient_type === 'COMPANY'" >
                        <payment-service-provider v-if="is_editable" />
                        <payment-receiver-name :editable="is_editable" />
                        <payment-receiver-id :editable="is_editable"  />
                    </template>

                    <template v-if="payment_plan.recipient_type === 'PERSON'" >
                        <cpr-look-up 
                            v-if="is_editable" 
                            :cpr.sync="payment_plan.recipient_id" 
                            :name.sync="payment_plan.recipient_name" />
                    </template>
                </div>

                <div v-if="payment_plan.recipient_type === 'PERSON'">
                    <payment-method :editable="is_editable" />
                    <payment-method-details v-if="payment_plan.payment_method === 'SD'" :editable="is_editable" />
                </div>

                <note :editable="is_editable" />

            </div>
            
            <fieldset v-if="is_editable" class="act-edit-actions">
                <hr>
                <input type="submit" value="Gem" style="margin-right: .5rem;">
                <button type="button" @click="reset">Fortryd</button>
            </fieldset>

        </form>

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
                                    <button type="button" class="modal-cancel-btn" @click="reload">Annullér</button>
                                    <button class="modal-delete-btn" type="submit">Slet</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
        
        <h2 style="padding: 2rem 0 0;">
            Betalinger <span style="opacity: .66;">betalingsnøgle {{ pay.payment_id }}</span>
        </h2>
        <payment-schedule :p-id="pay.payment_id" />
        
    </section>

</template>

<script>
import ActDisplayMixin from '../mixins/ActivityDisplayMixin.js'
import axios from '../http/Http.js'
import PaymentSchedule from '../payments/PaymentList.vue'
import PaymentServiceProvider from '../payments/edittypes/PaymentServiceProvider.vue'
import CprLookUp from '../forms/CprLookUp.vue'
import { json2jsDate } from '../filters/Date.js'
import { cost2da } from '../filters/Numbers.js'
import { activityId2name, sectionId2name, displayStatus, userId2name, approvalId2name } from '../filters/Labels.js'
import notify from '../notifications/Notify.js'
import UserRights from '../mixins/UserRights.js'
import PaymentInternalReceiver from '../payments/edittypes/PaymentInternalReceiverName.vue'

export default {

    mixins: [
        ActDisplayMixin,
        UserRights
    ],
    components: {
        PaymentSchedule,
        PaymentServiceProvider,
        CprLookUp,
        PaymentInternalReceiver
    },
    data: function() {
        return {
            payments: null,
            edit_mode: 'edit',
            showModal: false
        }
    },
    computed: {
        is_editable: function() {
            if (this.act && this.act.status !== 'GRANTED') {
                return true
            } else {
                return false
            }
        },
        pay: function() {
            return this.$store.getters.getPaymentPlan
        },
        cas: function() {
            return this.$store.getters.getCase
        },
        can_adjust: function() {
            // Adjust only if parent activity was granted ans has no other modifying activities
            if (this.appropriation && this.act.status === 'GRANTED') {
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
    watch: {
        cas: function() {
            if (this.cas && this.act.details) {
                this.$store.commit('setBreadcrumb', [
                    {
                        link: '/',
                        title: 'Sager'
                    },
                    {
                        link: `/case/${ this.cas.id }`,
                        title: `Hovedsag ${ this.cas.sbsys_id }, ${ this.cas.name }`
                    },
                    {
                        link: `/appropriation/${ this.appropriation.id }`,
                        title: `Bevillingsskrivelse ${ this.appropriation.sbsys_id }`
                    },
                    {
                        link: false,
                        title: `Udgift til ${ activityId2name(this.act.details) }`
                    }
                ])
            }
        }
    },
    methods: {
        reload: function() {
            this.showModal = false
            this.$store.dispatch('fetchActivity', this.$route.params.actId)
            .then(() => {
                this.$store.commit('setActDetail', this.act.details)
            })
        },
        displayDate: function(dt) {
            return json2jsDate(dt)
        },
        displayDigits: function(num) {
            return cost2da(num)
        },
        actId2name: function(id) {
            return activityId2name(id)
        },
        displaySection: function(id) {
            return sectionId2name(id)
        },
        statusLabel: function(status) {
            return displayStatus(status)
        },
        displayUserName: function(user_id) {
            return userId2name(user_id)
        },
        displayApprLevel: function(appr_lvl_id) {
            return approvalId2name(appr_lvl_id)
        },
        preDeleteCheck: function() {
            this.showModal = true
        },
        deleteActivity: function() {
            axios.delete(`/activities/${ this.$route.params.actId }/`)
            .then(res => {
                this.$router.push(`/appropriation/${ this.appropriation.id }`)
                notify('Ydelse slettet', 'success')
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        },
        checkDateMax: function(datestr) {
            const maxpast = parseInt( new Date().getFullYear() ) - 10,
                maxfuture = parseInt( new Date().getFullYear() ) + 18,
                date_regex = /[0-9]{4}-[0-9]{2}-[0-9]{2}/g
                
            if (!datestr.match(date_regex)) {
                notify('Er du sikker på, at du har angivet dato som åååå-mm-dd?', 'error')
                return false
            }
            if (parseInt(datestr.substr(0,4)) < maxpast) {
                notify('Dato må maks. være 10 år tilbage i tiden', 'error')
                return false
            } else if (parseInt(datestr.substr(0,4)) > maxfuture) {
                notify('Dato må maks. være 18 år fremme i tiden', 'error')
                return false
            } else {
                return true
            }
        },
        saveChanges: function() {

            if (!this.checkDateMax(this.act.start_date)) {
                return
            }
            if (this.act.end_date && !this.checkDateMax(this.act.end_date)) {
                return
            }

            let new_act = this.act
            new_act.payment_plan = this.payment_plan
            if (new_act.payment_plan.payment_type === 'ONE_TIME_PAYMENT') {
                new_act.end_date = new_act.start_date
            }

            axios.patch(`/activities/${ this.$route.params.actId }/`, new_act)
            .then(res => {
                this.$router.push(`/appropriation/${ this.appropriation.id }`)
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        },
        reset: function() {
            this.$router.push(`/appropriation/${ this.appropriation.id }`)
        }
    },
    created: function(){
        this.reload()
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
        grid-template-columns: repeat( auto-fit, minmax(20rem, 1fr) );
        gap: 2rem;
        margin-bottom: .25rem;
    }

    .act-edit-header > dl {
        margin: 0;
        border-right: 1px solid var(--grey0);
    }

    .act-edit-header > dl:last-child {
        border: none;
    }

    .act-edit-header > dl > dt {
        padding-top: 0;
    }

    .act-edit-form {
        padding: 1.5rem 2rem 2rem;
    }

    .act-edit-main {
        display: grid;
        grid-template-columns: repeat( auto-fit, minmax(20rem, 1fr) );
        gap: 2rem;
        padding: 0;
    }

    .act-edit-main > * {
        border-right: 1px solid var(--grey0);
        padding-right: 2rem;
    }

    .act-edit-actions {
        padding: 0;
        margin: 0;
    }

    .activity .payment_schedule {
        margin: 0 0 1rem;
    }

</style>