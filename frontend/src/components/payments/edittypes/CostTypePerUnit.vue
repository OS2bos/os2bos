<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div>

        <fieldset v-if="editable">

            <label class="required" for="pay-cost-pr-unit">Enhedspris</label>
            <input type="number" id="pay-cost-pr-unit" v-model="amount" required step="0.01"> kr

            <label for="pay-units" class="required">Antal</label>
            <input type="number" id="pay-units" v-model="units" required step="0.1">

            <label for="pay-cost-exec-date" class="required">Pris gælder fra dato</label>
            <input type="date" id="pay-cost-exec-date" v-model="start_date" required>
            
            <error :err-key="property" />

        </fieldset>

        <dl v-else>
            <dt>Enhedspris x antal</dt>
            <dd>{{ displayDigits(amount) }} kr x {{ units }}<br>({{ displayDigits((amount * units)) }} kr)</dd>
            <dt>Pris gælder fra</dt>
            <dd>{{ displayDate(start_date) }}</dd>
        </dl>

        <per-unit-history />

    </div>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { cost2da } from '../../filters/Numbers.js'
import { json2jsDate } from '../../filters/Date.js'
import PerUnitHistory from '../PaymentPerUnitHistory.vue'

export default {
    components: {
        Error,
        PerUnitHistory
    },
    mixins: [
        mixin
    ],
    computed: {
        amount: {
            get: function() {
                if (this.model) {
                    return this.model.amount
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
    methods: {
        displayDigits: function(num) {
            return cost2da(num)
        },
        displayDate: function(date) {
            return json2jsDate(date)
        }
    },
    created: function() {
        this.property = 'price_per_unit'
    }

}
</script>