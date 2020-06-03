<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="act-create-step">
        <h2>Beløb</h2>

        <cost-type :editable="true" />
        
        <template v-if="payment_plan.payment_cost_type === 'FIXED'">
            <cost-type-fixed :editable="true" />
        </template>

        <template v-if="payment_plan.payment_cost_type === 'RATE'">
            <cost-type-rate :editable="true" />
        </template>

        <template v-if="payment_plan.payment_cost_type === 'PER_UNIT'">
            <cost-type-per-unit :editable="true" />
        </template>

        <template v-if="payment_plan.payment_cost_type === 'PER_UNIT' || payment_plan.payment_cost_type === 'RATE'">
            <pay-plan-calc />
        </template>

    </div>
</template>

<script>
import CostType from '../../payments/edittypes/CostType.vue'
import CostTypeFixed from '../../payments/edittypes/CostTypeFixed.vue'
import CostTypeRate from '../../payments/edittypes/CostTypeRate.vue'
import CostTypePerUnit from '../../payments/edittypes/CostTypePerUnit.vue'
import PayPlanCalc from '../../payments/PaymentPlanCalc.vue'

export default {

    components: {
        CostType,
        CostTypeFixed,
        CostTypeRate,
        CostTypePerUnit,
        PayPlanCalc
    },
    computed: {
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        }
    }

}
</script>