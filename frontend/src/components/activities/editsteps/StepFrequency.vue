<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="act-create-step">
        <h2>Betalingsfrekvens</h2>

        <payment-type :editable="true" />

        <template v-if="payment_plan.payment_type === 'ONE_TIME_PAYMENT'">
            <pay-date-single :editable="true" />
            <fieldset>
                <legend>Betaling dækker periode</legend>
                <div class="row">
                    <pay-date-single-period-start :editable="true" />
                    <pay-date-single-period-end :editable="true" />
                </div>
            </fieldset>
        </template>

        <template v-if="payment_plan.payment_type === 'RUNNING_PAYMENT'">
            <pay-date-start :editable="true" />
            <pay-date-end :editable="true" />

            <payment-frequency :editable="true" />
        </template>

    </div>
</template>

<script>
import PaymentType from '../../payments/edittypes/PaymentType.vue'
import PayDateSingle from '../edittypes/PayDateSingle.vue'
import PayDateSinglePeriodStart from '../edittypes/PayDateSinglePeriodStart.vue'
import PayDateSinglePeriodEnd from '../edittypes/PayDateSinglePeriodEnd.vue'
import PayDateStart from '../edittypes/PayDateStart.vue'
import PayDateEnd from '../edittypes/PayDateEnd.vue'
import PaymentFrequency from '../../payments/edittypes/PaymentFrequency.vue'

export default {

    components: {
        PaymentType,
        PayDateSingle,
        PayDateSinglePeriodStart,
        PayDateSinglePeriodEnd,
        PayDateStart,
        PayDateEnd,
        PaymentFrequency
    },
    computed: {
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        }
    }

}
</script>