<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">

        <label class="required" for="field-rates">Takst</label>
        <select v-model="model" required id="field-rates">
            <option 
                v-for="choice in rate_choices"
                :key="choice.id"
                :value="choice.id"
                :title="choice.name">
                {{ truncateName(choice.name) }}
            </option>
        </select>

        <payment-units />
        
        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Takst x antal</dt>
        <dd>
            {{ displayRateName(model) }},<br>
            {{ displayRateAmount(model) }} kr x {{ units }}<br>
            ({{ model * units }} kr)
        </dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { rateId2details } from '../../filters/Labels.js'
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
        rate_choices: function() {
            return this.$store.getters.getRates
        },
        units: function(){
            return this.$store.getters.getPaymentPlanProperty('payment_units')
        }
    },
    methods: {
        truncateName: function(str) {
            if (str.length > 35) {
                return str.substr(0,30) + '...'
            } else {
                return str
            }
        },
        displayRateAmount: function(rate_id) {
            if (rateId2details(rate_id) !== '-') {
                return rateId2details(rate_id).rates_per_date[0].rate
            } else {
                return rateId2details(rate_id)
            }
            
        },
        displayRateName: function(rate_id) {
            return rateId2details(rate_id).name
        }
    },
    created: function() {
        this.property = 'payment_rate'
    }

}
</script>