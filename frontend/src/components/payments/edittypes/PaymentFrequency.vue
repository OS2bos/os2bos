<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable" class="payment-frequencies">
        <legend class="required">Betalingsfrekvens</legend>

        <div class="row">
            <div>
                <input 
                    type="radio" 
                    v-model="model"
                    id="pay_freq_month" 
                    name="pay_freq" 
                    value="MONTHLY" 
                    required>
                <label for="pay_freq_month">Månedligt</label>
            </div>
            <div v-if="model === 'MONTHLY'">
                <label for="pay_day_of_month">den</label>
                <select v-model="day_of_month" id="pay_day_of_month" required>
                    <option v-for="o in date_options" :value="o" :key="o">
                        {{ o }}.
                    </option>
                </select>
                <error err-key="payment_day_of_month" />
            </div>
        </div>

        <input 
            type="radio"
            v-model="model" 
            id="pay_freq_biweek" 
            name="pay_freq" 
            value="BIWEEKLY" 
            required>
        <label for="pay_freq_biweek">Hver 14. dag</label>

        <input 
            type="radio" 
            v-model="model"
            id="pay_freq_week" 
            name="pay_freq" 
            value="WEEKLY" 
            required>
        <label for="pay_freq_week">Ugentligt</label>

        <input 
            type="radio" 
            v-model="model"
            id="pay_freq_day" 
            name="pay_freq" 
            value="DAILY" 
            required>
        <label for="pay_freq_day">Dagligt</label>

        <error :err-key="property" />
        
    </fieldset>

    <dl v-else>
        <dt>Betalingsfrekvens</dt> 
        <dd>
            {{ dispPayFreq(model) }}
            <template v-if="day_of_month">
                - hver {{ day_of_month }}. dag i måneden
            </template>
        </dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { displayPayFreq } from '../../filters/Labels.js'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    data: function() {
        return {
            date_options: [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 23, 24, 25, 26, 27 ,28 ,29, 30, 31
            ]
        }
    },
    computed: {
        day_of_month: {
            get: function() {
                return this.$store.getters.getPaymentPlanProperty('payment_day_of_month')
            },
            set: function(new_val) {
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'payment_day_of_month',
                    val: new_val
                })
            }
        }
    },
    watch: {
        model: function(new_val) {

            /****** RULES ******/ 

            // Reset payment day of month if not monthly
            if (new_val !== 'MONTHLY') {
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'payment_day_of_month',
                    val: null
                })
            }
        }
    },
    methods: {
        dispPayFreq: function(freq) {
            return displayPayFreq(freq)
        }
    },
    created: function() {
        this.property = 'payment_frequency'
    }
}
</script>

<style>

    .payment-frequencies label[for="pay_day_of_month"] {
        display: inline;
        margin: 0 .5rem;
    }

</style>