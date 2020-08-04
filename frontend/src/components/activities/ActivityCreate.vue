<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="act-create">
        <h1>
            <i class="material-icons">style</i>
            Opret ydelse
        </h1>
        
        <div :class="`act-create-header activity-${ act.status }`">
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
        </div>

        <form @submit.prevent="" :class="`act-create-form activity-${ act.status }`">
            <div class="act-create-main">
                <step-activity class="row-item" />
                <step-frequency class="row-item" />
                <step-payment class="row-item" />
                <step-receiver class="row-item" />
            </div>
            <hr>
            <step-summary class="row-item" v-on:save="saveActivity" v-on:cancel="cancelCreate" />
        </form>
    
    </div>
</template>

<script>
import StepActivity from './editsteps/StepActivity.vue'
import StepFrequency from './editsteps/StepFrequency.vue'
import StepPayment from './editsteps/StepPayment.vue'
import StepReceiver from './editsteps/StepReceiver.vue'
import StepSummary from './editsteps/StepSummary.vue'
import axios from '../http/Http.js'
import store from '../../store.js'
import { sanitizeActivity } from './ActivitySave.js'

export default { 
    components: {
        StepActivity,
        StepFrequency,
        StepPayment,
        StepReceiver,
        StepSummary
    },
    computed: {
        cas: function() {
            return this.$store.getters.getCase
        },
        appropriation: function() {
            return this.$store.getters.getAppropriation
        },
        act: function() {
            return this.$store.getters.getActivity
        },
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        }
    },
    beforeRouteEnter: function(to, from, next) {
        if (to.query.mode !== 'expected') {
            let new_act = { 
                status: 'DRAFT',
                appropriation: from.params.apprId
            }
            if (to.query.type === 'main') {
                new_act.activity_type = 'MAIN_ACTIVITY'
            } else {
                new_act.activity_type = 'SUPPL_ACTIVITY'
            }
            store.commit('clearPaymentPlan')
            store.commit('setActivity', new_act)
        } else if (to.query.mode === 'expected') {
            const act = store.state.activity.activity,
                  pay_plan = store.state.activity.activity.payment_plan
            
            let new_act = {
                status: 'EXPECTED',
                modifies: act.id,
                note: act.note,
                details: act.details,
                activity_type: act.activity_type,
                appropriation: act.appropriation,
                payment_plan: {
                    recipient_type: pay_plan.recipient_type,
                    recipient_id: pay_plan.recipient_id,
                    recipient_name: pay_plan.recipient_name,
                    payment_method: pay_plan.payment_method,
                    payment_frequency: pay_plan.payment_frequency,
                    payment_date: pay_plan.payment_date,
                    payment_day_of_month: pay_plan.payment_day_of_month,
                    payment_type: pay_plan.payment_type,
                    payment_units: pay_plan.payment_units,
                    payment_amount: pay_plan.payment_amount,
                    fictive: pay_plan.fictive,
                    payment_method_details: pay_plan.payment_method_details
                }
            }
            store.commit('setActivity', new_act)
        }
        next()
    },
    methods: {
        checkDateMax: function(datestr) {
            const maxpast = parseInt( new Date().getFullYear() ) - 10,
                maxfuture = parseInt( new Date().getFullYear() ) + 18,
                date_regex = /[0-9]{4}-[0-9]{2}-[0-9]{2}/g
            if (!datestr) {
                return false
            }    
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
        cleanAndExit: function() {
            this.$store.commit('clearActivity')
            this.$store.commit('clearPaymentPlan')
            this.$router.push(`/appropriation/${ this.appropriation.id }/`)
        },
        saveActivity: function() {
            if (this.act.start_date && !this.checkDateMax(this.act.start_date)) {
                return
            }
            if (this.act.end_date && !this.checkDateMax(this.act.end_date)) {
                return
            }

            let new_act = this.act

            new_act.payment_plan = this.payment_plan

            if (this.$route.query.mode !== 'expected') {
                // Clean up null valued items in new_act
                for (let prop in new_act) {
                    if (new_act[prop] === null) {
                        delete new_act[prop]
                    }
                }
                for (let prop in new_act.payment_plan) {
                    if (new_act.payment_plan[prop] === null) {
                        delete new_act.payment_plan[prop]
                    }
                }
            } else {
                // We are POSTing an EXPECTED activity
                delete new_act.payment_plan.id // Don't try to overwrite previous payment_plan
            }

            const sanitized_act = sanitizeActivity(new_act, 'post')

            axios.post('/activities/', sanitized_act)
            .then(res => {
                this.cleanAndExit()
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))            
        },
        cancelCreate: function() {
            this.cleanAndExit()
        }
    }
}
</script>

<style>

    .act-create {
        padding: 0 2rem 2rem;
    }

    .act-create-header {
        background-color: var(--grey1);
        padding: 1rem 2rem;
        display: grid;
        grid-template-columns: repeat( auto-fill, minmax(20rem, 1fr) );
        gap: 2rem;
        margin-bottom: .25rem;
    }

    .act-create-header > dl {
        border-right: solid 1px var(--grey0);
        margin: 0;
    }

    .act-create-header > dl > dt {
        padding-top: 0;
    }

    .act-create-form {
        padding: .5rem 2rem 0;
    }

    .act-create-main {
        display: grid;
        margin-top: .25rem;
        grid-template-columns: repeat( auto-fill, minmax(20rem, 1fr) );
        gap: 2rem;
    }

    .act-create-main > * {
        border-right: solid 1px var(--grey0);
    }

    .act-create-step {
        padding-right: 2rem;
    }

    .act-create-nav > a {
        margin-right: 2rem;
    }

    .activity-EXPECTED {
        background-color: hsl(40, 90%, 80%);
    }

</style>