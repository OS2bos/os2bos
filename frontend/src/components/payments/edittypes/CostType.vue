<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">
        <legend class="required">Vælg afregningsenhed</legend>
        
        <input type="radio" v-model="model" id="pay-cost-type-rate" required value="GLOBAL_RATE" name="cost-type" @change="resetValues">
        <label for="pay-cost-type-rate">Takst</label>

        <template v-if="payment_plan.payment_type !== 'ONE_TIME_PAYMENT'">
            <input type="radio" v-model="model" id="pay-cost-type-per-unit" required value="PER_UNIT" name="cost-type" @change="resetValues">
            <label for="pay-cost-type-per-unit">Enhedspris</label>
        </template>

        <input type="radio" v-model="model" id="pay-cost-type-fixed" required value="FIXED" name="cost-type" @change="resetValues">
        <label for="pay-cost-type-fixed">Beløb</label>

        <error :err-key="property" />
    </fieldset>

    <dl v-else>
        <dt>Afregningsenhed</dt>
        <dd>{{ dispCostType(model) }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { displayCostType } from '../../filters/Labels.js'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    computed: {
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        }
    },
    methods: {
        dispCostType: function(type) {
            return displayCostType(type)
        },
        resetValues: function() {
            this.$store.commit('setPaymentPlanProperty', { 
                prop: 'price_per_unit',
                val: null
            })
            this.$store.commit('setPaymentPlanProperty', { 
                prop: 'payment_rate',
                val: null
            })
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'payment_units',
                val: null
            })
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'payment_amount',
                val: null
            })
        }
    },
    created: function() {
        this.property = 'payment_cost_type'
    }
}
</script>