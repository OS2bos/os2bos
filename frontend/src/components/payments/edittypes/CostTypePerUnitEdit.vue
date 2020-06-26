<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div>

        <fieldset v-if="editable">

            <payment-units />

            <label class="required" for="pay-cost-pr-unit">Enhedspris</label>
            <input type="number" id="pay-cost-pr-unit" v-model="amount" required step="0.01"> kr

            <label for="pay-cost-exec-date" class="required">Pris gælder fra dato</label>
            <input type="date" id="pay-cost-exec-date" v-model="start_date" required>
            
            <error :err-key="property" />

        </fieldset>

    </div>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { cost2da } from '../../filters/Numbers.js'
import { json2jsDate } from '../../filters/Date.js'
import PaymentUnits from './PaymentUnits.vue'

export default {
    components: {
        Error,
        PaymentUnits
    },
    mixins: [
        mixin
    ],
    computed: {
        amount: {
            get: function() {
                if (this.model) {
                    let mdl = this.model
                    return mdl.current_amount ? mdl.current_amount : mdl.amount
                }
            },
            set: function(new_val) {
                if (this.model === null) {
                    this.model = {
                        amount: new_val,
                        start_date: null
                    }
                } else {
                    this.model.amount = new_val
                }
            }
        },
        units: function(){
            return this.$store.getters.getPaymentPlanProperty('payment_units')
        },
        start_date: {
            get: function() {
                if (this.model) {
                    return this.model.start_date
                }
            },
            set: function(new_val) {
                if (this.model === null) {
                    this.model = {
                        amount: null,
                        start_date: new_val
                    }
                } else {
                    this.model.start_date = new_val
                }
            }
        }
    },
    created: function() {
        this.property = 'price_per_unit'
    }
}
</script>