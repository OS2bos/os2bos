<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">

        <label class="required" for="pay-cost-pr-unit">Enhedspris</label>
        <input type="number" id="pay-cost-pr-unit" v-model="model" required step="0.01"> kr

        <label for="pay-units" class="required">Antal</label>
        <input type="number" id="pay-units" v-model="units" required step="0.1">

        <label for="pay-cost-exec-date" class="required">Pris gælder fra dato</label>
        <input type="date" id="pay-cost-exec-date" v-model="exec_date" required>
        
        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Enhedspris x antal</dt>
        <dd>{{ displayDigits(model) }} x {{ units }} kr</dd>
        <dt>Pris gælder fra</dt>
        <dd>{{ exec_date }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { cost2da } from '../../filters/Numbers.js'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    computed: {
        units: {
            get: function() {
                return this.$store.getters.getPaymentPlanProperty('payment_units')
            },
            set: function(new_val) {
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'payment_units',
                    val: new_val
                })
            }
        },
        exec_date: {
            get: function() {
                return this.$store.getters.getPaymentPlanProperty('payment_pricing_date')
            },
            set: function(new_val) {
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'payment_pricing_date',
                    val: new_val
                })
            }
        }
    },
    methods: {
        displayDigits: function(num) {
            return cost2da(num)
        }
    },
    created: function() {
        this.property = 'payment_amount'
    }

}
</script>