<template>

    <section class="activity" v-if="act">
        <header class="activity-header">
            <h1>
                <i class="material-icons">style</i>
                Udgift til {{ activityId2name(act.details) }}
            </h1>
            <button v-if="act.status !== 'GRANTED'" @click="show_edit = !show_edit" class="act-edit-btn">Redigér</button>
            <button v-if="act.status === 'GRANTED'" @click="createExpected()" class="act-edit-btn">+ Lav forventet justering</button>
        </header>

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
            
            <dl v-if="pay">
                <h3>Beløb</h3>
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
                <dd>{{ pay.payment_amount }} kr.</dd>
            </dl>
            <dl v-if="pay">
                <h3>Betales til</h3>
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
            <dl v-if="pay">
                <h3>Betaling</h3>
                <dt>Betalingsmåde</dt>
                <dd>
                    <div v-if="pay.payment_method === 'INVOICE'">Faktura</div>
                    <div v-if="pay.payment_method === 'INTERNAL'">Intern afregning</div>
                    <div v-if="pay.payment_method === 'CASH'">Kontant udbetaling</div>
                    <div v-if="pay.payment_method === 'SD'">SD-løn</div>
                </dd>
            </dl>

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
    import { activityId2name, sectionId2name, displayStatus } from '../filters/Labels.js'

    export default {

        components: {
            ActivityEdit,
            PaymentSchedule
        },
        data: function() {
            return {
                payments: null,
                show_edit: false,
                edit_mode: 'edit'
            }
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
                this.show_edit =  false
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
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
            }
        },
        created: function() {
            this.$store.dispatch('fetchActivity', this.$route.params.id)
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

</style>
