<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="act-create-step" v-if="!is_individual_payment_type(payment_plan)">
        <h2>Beløb</h2>

        <cost-type :editable="true" />
        
        <template v-if="payment_plan.payment_cost_type === 'FIXED'">
            <cost-type-fixed :editable="true" />
        </template>

        <template v-if="payment_plan.payment_cost_type === 'GLOBAL_RATE'">
            <payment-units :editable="true" />
            <cost-type-rate :editable="true" />
        </template>

        <template v-if="payment_plan.payment_cost_type === 'PER_UNIT'">
            <payment-units :editable="true" />
            <cost-type-per-unit-edit :editable="true" />
        </template>

        <pay-plan-calc />

    </div>
</template>

<script>
import CostType from '../../payments/edittypes/CostType.vue'
import CostTypeFixed from '../../payments/edittypes/CostTypeFixed.vue'
import CostTypeRate from '../../payments/edittypes/CostTypeRate.vue'
import CostTypePerUnitEdit from '../../payments/edittypes/CostTypePerUnitEdit.vue'
import PayPlanCalc from '../../payments/PaymentPlanCalc.vue'
import PaymentUnits from '../../payments/edittypes/PaymentUnits.vue'
import PermissionLogic from '../../mixins/PermissionLogic.js'

export default {

    components: {
        CostType,
        CostTypeFixed,
        CostTypeRate,
        PayPlanCalc,
        CostTypePerUnitEdit,
        PaymentUnits
    },
    mixins: [
        PermissionLogic
    ],
    computed: {
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        }
    }

}
</script>