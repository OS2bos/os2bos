<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <dl v-if="model">
        <dt>Enhedspris x antal</dt>
        <dd class="perunitdisplay" v-html="displayPriceRate(model, units)"></dd>
        <dt>Enhedspris gælder</dt>
        <dd>{{ displayPriceDate(model) }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { cost2da } from '../../filters/Numbers.js'
import { json2jsDate, epoch2DateStr } from '../../filters/Date.js'
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
        getBestRate: function(price_per_unit) {
            if (price_per_unit.rates_per_date) {
                return price_per_unit.rates_per_date.find(function(rate) {
                        return rate.start_date >= epoch2DateStr(new Date())
                })
            } else {
                return {
                    rate: price_per_unit.amount,
                    start_date: price_per_unit.start_date
                }
            }
        },
        displayPriceRate: function(price_per_unit, units) {
            const current = this.getBestRate(price_per_unit)
            return `${ this.displayDigits(current.rate) } kr x ${ this.displayDigits(units) }<br> ( ${ this.displayDigits(units * current.rate) } kr)`
        },
        displayPriceDate: function(price_per_unit) {
            const current = this.getBestRate(price_per_unit)
            return `${ json2jsDate(current.start_date) } - ${ json2jsDate(current.end_date) }`
        }
    },
    created: function() {
        this.property = 'price_per_unit'
    }
}
</script>