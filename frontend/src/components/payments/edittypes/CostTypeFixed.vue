<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset class="payment-type-single" v-if="editable">

        <label class="required" for="field-amount-1">Beløb</label>
        <input v-model="model" type="number" step="0.01" required id="field-amount-1"> kr
        
        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Beløb</dt>
        <dd>{{ displayDigits(model) }} kr</dd>
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