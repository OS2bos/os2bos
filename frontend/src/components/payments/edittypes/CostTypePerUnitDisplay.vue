<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <dl v-if="model">
        <dt>Enhedspris x antal</dt>
        <dd v-if="model.current_amount" class="perunitdisplay">
            {{ displayDigits(model.current_amount) }} kr x {{ displayDigits(units) }}<br>
            ({{ displayDigits((model.current_amount * units)) }} kr)
        </dd>
        <dd v-else>
            {{ model.amount ? displayDigits(model.amount) : '-' }} kr x {{ displayDigits(units) }}<br>
            ({{ model.amount ? displayDigits((model.amount * units)) : '-' }} kr)
        </dd>
        <dt>Enhedspris gælder</dt>
        <dd v-if="model.start_date">
            Fra {{ displayDate(model.start_date) }}
        </dd>
        <dd v-else>
            {{ displayCurrentDates(model) }}
        </dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { cost2da } from '../../filters/Numbers.js'
import { json2jsDate } from '../../filters/Date.js'
import PerUnitHistory from '../PaymentPerUnitHistory.vue'
import PaymentUnits from './PaymentUnits.vue'

export default {
    components: {
        Error,
        PerUnitHistory,
        PaymentUnits
    },
    mixins: [
        mixin
    ],
    computed: {
        amount: function(){
            if (this.model) {
                return this.model.amount
            }
        },
        units: function(){
            return this.$store.getters.getPaymentPlanProperty('payment_units')
        },
        start_date: function() {
            if (this.model) {
                return this.model.start_date
            }
        }
    },
    methods: {
        displayDigits: function(num) {
            return cost2da(num)
        },
        displayDate: function(date) {
            return json2jsDate(date)
        },
        displayCurrentDates: function(price_per_unit) {
            if (price_per_unit.rates_per_date) {
                const current = price_per_unit.rates_per_date.find(function(rate) {
                    return parseFloat(rate.rate) === parseFloat(price_per_unit.current_amount)
                })
                if (current) {
                    return `${ json2jsDate(current.start_date) } - ${ json2jsDate(current.end_date) }`
                } else {
                    return `${ json2jsDate(price_per_unit.rates_per_date[0].start_date) } - ${ json2jsDate(price_per_unit.rates_per_date[0].end_date) }`
                }
                
            }   
        }
    },
    created: function() {
        this.property = 'price_per_unit'
    }
}
</script>