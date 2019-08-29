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
            </h1>
            <button v-if="act.status !== 'GRANTED'" @click="show_edit = !show_edit" class="act-edit-btn">Redigér</button>
            <button v-if="act.status === 'GRANTED'" @click="createExpected()" class="act-edit-btn">+ Lav forventet justering</button>
            <button v-if="act.status !== 'GRANTED'" class="act-delete-btn" @click="preDeleteCheck()">Slet</button>
        </header>

        <div v-if="showModal">
            <form @submit.prevent="deleteActivity()" class="modal-form">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div class="modal-container">

                            <div class="modal-header">
                                <slot name="header">
                                    <h1>Slet</h1>
                                </slot>
                            </div>

                            <div class="modal-body">
                                <slot name="body">
                                    <h3>
                                        Er du sikker på, at du vil slette denne
                                        <span v-if="act.status === 'DRAFT'">kladde</span>
                                        <span v-if="act.status === 'EXPECTED'">forventning</span> ?
                                    </h3>
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
                <dt>
                    Type
                </dt>
                <dd>
                    <div v-if="act.activity_type === 'MAIN_ACTIVITY'">Hovedydelse</div>
                    <div v-if="act.activity_type === 'SUPPL_ACTIVITY'">Følgeydelse</div>
                </dd>
                <dt>Bevilges efter §</dt>
                <dd v-if="appr">{{ displaySection(appr.section) }}</dd>
                <dt>Aktivitet</dt>
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
                        <div v-if="pay.payment_frequency === 'MONTHLY'">Månedligt</div>
                    </dd>
                    <dt>
                        <div v-if="pay.payment_type === 'PER_HOUR_PAYMENT'">Timer</div>
                        <div v-if="pay.payment_type === 'PER_DAY_PAYMENT'">Døgn</div>
                        <div v-if="pay.payment_type === 'PER_KM_PAYMENT'">Kilometer</div>
                    </dt>
                    <dd v-if="pay.payment_type === 'PER_HOUR_PAYMENT' || pay.payment_type === 'PER_DAY_PAYMENT' || pay.payment_type === 'PER_KM_PAYMENT'">
                        {{ pay.payment_units }}
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
                </dl>
            </div>

        </div>
        <div class="payment-schedule" v-if="!show_edit">
            <payment-schedule :payments="pay.payments" />
        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityEdit from './ActivityEdit.vue'
    import PaymentSchedule from '../payment/PaymentSchedule.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, sectionId2name, displayStatus } from '../filters/Labels.js'
    import store from '../../store.js'
    import notify from '../notifications/Notify.js'

    export default {

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
            }
        },
        watch: {
            cas: function() {
                if (this.cas) {
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
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
            createExpected: function() {                
                this.edit_mode = 'clone'
                this.show_edit =  true
            },
            preDeleteCheck: function() {
                 if (this.appr.activities.length > 0) {
                    this.showModal = true
                } else {
                    alert('Fejl')
                }
            },
            deleteActivity: function() {
                axios.delete(`/activities/${ this.$route.params.actId }`)
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
        margin: 1rem;
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

    .activity .act-delete-btn {
        margin: 0;
        border: solid .125rem var(--danger);
        color: var(--danger);
    }

    .activity .act-delete-btn:active {
        background-color: var(--danger);
    }

    .activity-info {
        display: grid; 
        grid-template-columns: auto auto auto auto;
        grid-gap: 3rem;
        justify-content: start;
        background-color: var(--grey1);
        padding: 1.5rem 2rem 2rem;
    }

     .payment-schedule {
        margin: 1rem;
    }

    .modal-delete-btn {
        float: right;
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--danger);
        border-color: var(--danger);
    }

    .modal-delete-btn:active {
        background-color: var(--danger);
    }

</style>
