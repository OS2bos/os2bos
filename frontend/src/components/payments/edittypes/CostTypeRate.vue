<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div>
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

        <dl style="margin-bottom: 1rem;">
            <dt>Takst x antal</dt>
            <dd>
                {{ displayRateName(model) }},<br>
                {{ displayCost(displayRateAmount(model)) }} kr x {{ units }}<br>
                ({{ displayCost( displayRateAmount(model) * units ) }} kr)
            </dd>
        </dl>
    </div>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { rateId2details } from '../../filters/Labels.js'
import { cost2da } from '../../filters/Numbers.js'
import PaymentUnits from './PaymentUnits.vue'
import { isCurrent } from '../../filters/Date.js'

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
        displayCost: function(cost) {
            return cost2da(cost)
        },
        displayRateAmount: function(rate_id) {
            const rate_data = rateId2details(rate_id),
                  today = new Date()
            if (rate_data !== '-') {
                let current_rate = rate_data.rates_per_date.find(function(rate) {
                    return isCurrent(rate.start_date, rate.end_date)
                })
                return current_rate.rate
            } else {
                return rate_data
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