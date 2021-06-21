<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section class="activity-edit">
        <header class="activity-edit-header">
            <h2>Redigér ydelse</h2>
        </header>
        <form @submit.prevent="saveChanges" class="activity-edit-form" v-if="act">
           
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

                        <fieldset v-if="is_editable">
                            <legend>Betaling dækker periode</legend>
                            <div class="row">
                                <pay-date-single-period-start :editable="true" />
                                <pay-date-single-period-end :editable="true" />
                            </div>
                        </fieldset>

                        <pay-date-single-period-display v-else />

                    </template>
                    <div v-if="payment_plan.payment_type !== 'ONE_TIME_PAYMENT'">
                        <pay-date-start :editable="is_editable" />
                        <pay-date-end :editable="is_editable" />
                    </div>
                    <div v-if="payment_plan.payment_type === 'RUNNING_PAYMENT'">
                        <payment-frequency :editable="is_editable" />
                    </div>
                </div>

                <div v-if="!is_individual_payment_type(payment_plan)">
                    <cost-type :editable="false" />
                    <template v-if="payment_plan.payment_cost_type === 'FIXED'">
                        <cost-type-fixed :editable="is_editable" />
                    </template>
                    <template v-if="payment_plan.payment_cost_type === 'GLOBAL_RATE'">
                        <payment-units :editable="is_editable" />
                        <cost-type-rate :editable="is_editable" />
                    </template>
                    <template v-if="payment_plan.payment_cost_type === 'PER_UNIT'">
                        <payment-units :editable="is_editable" />
                        <cost-type-per-unit-display />
                        <per-unit-history :editable="is_editable"/>
                    </template>
                </div>

                <div>
                    <payment-receiver-type :editable="false" />

                    <template v-if="payment_plan.recipient_type === 'INTERNAL'" >
                        <payment-internal-receiver :editable="is_editable" /> 
                        <payment-receiver-id :editable="is_editable" />
                    </template>

                    <template v-if="payment_plan.recipient_type === 'COMPANY'" >
                        <cvr-select />
                        <!--
                        <payment-service-provider v-if="is_editable" />
                        <payment-receiver-name :editable="is_editable" />
                        <payment-receiver-id :editable="is_editable"  />
                        -->
                    </template>

                    <template v-if="payment_plan.recipient_type === 'PERSON'" >
                        <cpr-look-up 
                            v-if="is_editable" 
                            :cpr.sync="payment_plan.recipient_id" 
                            :name.sync="payment_plan.recipient_name" />
                    </template>

                    <payment-method :editable="is_editable && payment_plan.recipient_type === 'PERSON'" />
                </div>

                <div v-if="payment_plan.recipient_type === 'PERSON'">
                    <payment-method-details v-if="payment_plan.payment_method === 'SD'" :editable="is_editable" />
                </div>

                <note :editable="is_editable" />

            </div>
        
            <fieldset v-if="is_editable" class="act-edit-actions">
                <hr>
                <input type="submit" value="Gem" style="margin-right: .5rem;">
                <button type="button" @click="reset">Annullér</button>
            </fieldset>

        </form>
    </section>

</template>

<script>
import ActDisplayMixin from '../mixins/ActivityDisplayMixin.js'
import axios from '../http/Http.js'
import PaymentServiceProvider from '../payments/edittypes/PaymentServiceProvider.vue'
import CprLookUp from '../forms/CprLookUp.vue'
import { json2jsDate } from '../filters/Date.js'
import { userId2name, approvalId2name } from '../filters/Labels.js'
import notify from '../notifications/Notify.js'
import PaymentInternalReceiver from '../payments/edittypes/PaymentInternalReceiverName.vue'
import PaymentUnits from '../payments/edittypes/PaymentUnits.vue'
import { sanitizeActivity } from './ActivitySave.js'
import PermissionLogic from '../mixins/PermissionLogic.js'
import CvrSelect from '../payments/edittypes/CVR_select.vue'


export default {

    mixins: [
        ActDisplayMixin,
        PermissionLogic
    ],
    components: {
        PaymentServiceProvider,
        CprLookUp,
        PaymentInternalReceiver,
        PaymentUnits,
        CvrSelect
    },
    computed: {
        is_editable: function() {
            if (this.act && this.act.status !== 'GRANTED') {
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        displayDate: function(dt) {
            return json2jsDate(dt)
        },
        displayUserName: function(user_id) {
            return userId2name(user_id)
        },
        displayApprLevel: function(appr_lvl_id) {
            return approvalId2name(appr_lvl_id)
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

            if (this.act.start_date && !this.checkDateMax(this.act.start_date)) {
                return
            }
            if (this.act.end_date && !this.checkDateMax(this.act.end_date)) {
                return
            }

            let new_act = this.act
            new_act.payment_plan = this.payment_plan
            delete new_act.payment_plan.price_per_unit // API endpoint won't accept this in PATCH request

            const sanitized_act = sanitizeActivity(new_act, 'patch')

            axios.patch(`/activities/${ this.$route.params.actId }/`, sanitized_act)
            .then(res => {
                this.$emit('save')
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        },
        reset: function() {
            this.$emit('cancel')
        }
    }
}
    
</script>

<style>

    .activity-edit {
        margin: 0 0 1rem;
    }

    .activity-edit-header {
        background-color: var(--grey2);
        padding: .5rem 2rem;
    }

    .activity-edit-form {
        padding: 0;
    }

    .act-edit-main {
        display: grid;
        grid-template-columns: repeat( auto-fill, minmax(20rem, 1fr) );
        gap: 2rem;
        padding: 1.5rem 2rem 2rem;
    }

    .act-edit-main > * {
        border-right: 1px solid var(--grey0);
        padding-right: 2rem;
    }

    .act-edit-actions {
        padding: 0 2rem 2rem;
        margin: 0;
    }

    .act-edit-actions hr {
        margin: 0 0 2rem;
    }

    .activity-EXPECTED .activity-edit-header {
        background-color: hsl(40, 90%, 70%);
    }

    .activity-EXPECTED .activity-edit-form {
        background-color: hsl(40, 90%, 80%);
    }

</style>