<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="activity" v-if="act">
        <header class="activity-header">
            <h1>
                <i class="material-icons">style</i>
                Udgift til {{ activityId2name(act.details) }}
                <span v-if="act.payment_plan.fictive" class="dim">(Fiktiv)</span>
            </h1>
            <template v-if="permissionCheck === true">
                <button v-if="act.status !== 'GRANTED'" @click="show_edit = !show_edit" class="act-edit-btn">Redigér</button>
                <button v-if="can_adjust" @click="createExpected()" class="act-edit-btn">+ Lav forventet justering</button>
                <button v-if="act.status !== 'GRANTED'" class="act-delete-btn" @click="preDeleteCheck()">Slet</button>
            </template>
        </header>

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
                                    <button type="button" class="modal-cancel-btn" @click="reload()">Annullér</button>
                                    <button class="modal-delete-btn" type="submit">Slet</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <div v-if="show_edit">
            <activity-edit :activity-obj="act" v-if="show_edit" @save="reload()" @close="show_edit = !show_edit" :mode="edit_mode" />
        </div>

        <div class="activity-info" v-if="!show_edit">
            <dl>
                <dt>Status</dt>
                <dd>
                    <div v-html="statusLabel(act.status)"></div>
                </dd>
                <template v-if="act.status === 'GRANTED'">
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
                </template>
                <dt>
                    Type
                </dt>
                <dd>
                    <div v-if="act.activity_type === 'MAIN_ACTIVITY'">Hovedydelse</div>
                    <div v-if="act.activity_type === 'SUPPL_ACTIVITY'">Følgeydelse</div>
                </dd>
                <dt>Bevilges efter §</dt>
                <dd v-if="appr">{{ displaySection(appr.section) }}</dd>
                <dt>Ydelse</dt>
                <dd>{{ activityId2name(act.details) }}</dd>
                <dt>Startdato</dt>
                <dd>{{ displayDate(act.start_date) }}</dd>
                <template v-if="act.end_date">
                    <dt>Slutdato</dt>
                    <dd>{{ displayDate(act.end_date) }}</dd>
                </template>
                <template v-if="act.note">
                    <dt>Supplerende information</dt>
                    <dd>{{ act.note }}</dd>
                </template>
            </dl>
            
            <div v-if="pay">
                <dl>
                    <dt>Afregningsenhed</dt>
                    <dd>
                        <div v-if="pay.payment_type === 'ONE_TIME_PAYMENT'">Engangsudgift</div>
                        <div v-if="pay.payment_type === 'RUNNING_PAYMENT'">Fast beløb, løbende</div>
                        <div v-if="pay.payment_type === 'PER_HOUR_PAYMENT'">Takst pr. time</div>
                        <div v-if="pay.payment_type === 'PER_DAY_PAYMENT'">Takst pr. døgn</div>
                        <div v-if="pay.payment_type === 'PER_KM_PAYMENT'">Takst pr. kilometer</div>
                    </dd>
                    <dd>
                        <div v-if="pay.payment_frequency === 'DAILY'">Dagligt</div>
                        <div v-if="pay.payment_frequency === 'WEEKLY'">Ugentligt</div>
                        <div v-if="pay.payment_frequency === 'BIWEEKLY'">Hver 2. uge</div>
                        <div v-if="pay.payment_frequency === 'MONTHLY'">Månedligt den {{pay.payment_day_of_month}}.</div>
                    </dd>
                    <dt>
                        <div v-if="pay.payment_type === 'PER_HOUR_PAYMENT'">Timer</div>
                        <div v-if="pay.payment_type === 'PER_DAY_PAYMENT'">Døgn</div>
                        <div v-if="pay.payment_type === 'PER_KM_PAYMENT'">Kilometer</div>
                    </dt>
                    <dd v-if="pay.payment_type === 'PER_HOUR_PAYMENT' || pay.payment_type === 'PER_DAY_PAYMENT' || pay.payment_type === 'PER_KM_PAYMENT'">
                        {{ displayDigits(pay.payment_units) }}
                    </dd>
                    <dt>Beløb</dt>
                    <dd>{{ displayDigits(pay.payment_amount) }} kr.</dd>
                </dl>
            </div>
            <div v-if="pay">
                <dl>
                    <dt>Betalingsmodtager</dt>
                    <dd>
                        <div v-if="pay.recipient_type === 'INTERNAL'">Intern</div>
                        <div v-if="pay.recipient_type === 'COMPANY'">Firma</div>
                        <div v-if="pay.recipient_type === 'PERSON'">Person</div>
                    </dd>
                    <dt>
                        <div v-if="pay.recipient_type === 'INTERNAL'">Reference</div>
                        <div v-if="pay.recipient_type === 'COMPANY'">CVR-nr</div>
                        <div v-if="pay.recipient_type === 'PERSON'">CPR-nr</div>
                    </dt>
                    <dd>{{ pay.recipient_id }}</dd>
                    <dt>Navn</dt>
                    <dd>{{ pay.recipient_name }}</dd>
                </dl>
            </div>
            <div v-if="pay">
                <dl>
                    <dt>Betalingsmåde</dt>
                    <dd>
                        <div v-if="pay.payment_method === 'INVOICE'">Faktura</div>
                        <div v-if="pay.payment_method === 'INTERNAL'">Intern afregning</div>
                        <div v-if="pay.payment_method === 'CASH'">Kontant udbetaling</div>
                        <div v-if="pay.payment_method === 'SD'">SD-løn</div>
                    </dd>
                    <template v-if="pay.payment_method_details === 1">
                        <dt>Skattekort</dt>
                        <dd>Hovedkort</dd>
                    </template>
                    <template v-if="pay.payment_method_details === 2">
                        <dt>Skattekort</dt>
                        <dd>Bikort</dd>
                    </template>
                    <template v-if="pay.fictive">
                        <dt>Betaling</dt>
                        <dd>Fiktiv</dd>
                    </template>
                </dl>
            </div>

        </div>
        
        <h2 style="padding: 2rem 0 0;">
            Betalingsnøgle {{ pay.payment_id }}
        </h2>
        <payment-schedule :p-id="pay.payment_id" v-if="!show_edit" />
        
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityEdit from './ActivityEdit.vue'
    import PaymentSchedule from '../payments/PaymentList.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, sectionId2name, displayStatus, userId2name, approvalId2name } from '../filters/Labels.js'
    import store from '../../store.js'
    import notify from '../notifications/Notify.js'
    import UserRights from '../mixins/UserRights.js'

    export default {

        mixins: [UserRights],

        components: {
            ActivityEdit,
            PaymentSchedule
        },
        data: function() {
            return {
                payments: null,
                show_edit: false,
                edit_mode: 'edit',
                showModal: false
            }
        },
        beforeRouteEnter: function(to, from, next) {
            store.commit('clearActivity')
            store.dispatch('fetchActivity', to.params.actId)
            .then(() => next())
        },
        beforeRouteUpdate: function(to, from, next) {
            store.dispatch('fetchActivity', to.params.actId)
            .then(() => next())
        },
        computed: {
            act: function() {
                return this.$store.getters.getActivity
            },
            pay: function() {
                return this.$store.getters.getPaymentSchedule
            },
            appr: function() {
                return this.$store.getters.getAppropriation
            },
            cas: function() {
                return this.$store.getters.getCase
            },
            can_adjust: function() {
                // Adjust only if parent activity was granted ans has no other modifying activities
                if (this.appr && this.act.status === 'GRANTED') {
                    let modifier = this.appr.activities.filter(ac => {
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
                if (this.cas) {
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
                            link: `/appropriation/${ this.appr.id }`,
                            title: `Bevillingsskrivelse ${ this.appr.sbsys_id }`
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
                this.show_edit =  false
                this.$store.dispatch('fetchActivity', this.$route.params.actId)
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            activityId2name: function(id) {
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
            createExpected: function() {                
                this.edit_mode = 'clone'
                this.show_edit =  true
            },
            preDeleteCheck: function() {
                this.showModal = true
            },
            deleteActivity: function() {
                axios.delete(`/activities/${ this.$route.params.actId }/`)
                .then(res => {
                    this.$router.push(`/appropriation/${ this.appr.id }`)
                    notify('Ydelse slettet', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            }
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
    .modal-delete-btn {
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

    .activity-info {
        display: grid; 
        grid-template-columns: auto auto auto auto;
        grid-gap: 3rem;
        justify-content: start;
        background-color: var(--grey1);
        padding: 1.5rem 2rem 2rem;
    }

    .activity .payment_schedule {
        margin: 0 0 1rem;
    }

</style>
