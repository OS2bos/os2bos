<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">

        <label class="required" for="field-amount-1">Takst</label>
        <select v-model="model" required id="field-amount-1">
            <option 
                v-for="choice in rate_choices"
                :key="choice.id"
                :value="choice.id">
                {{ choice.name }}
            </option>
        </select>

        <label for="pay-units" class="required">Antal</label>
        <input type="number" id="pay-units" v-model="units" required step="0.1">
        
        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Takst x antal</dt>
        <dd>
            {{ model }} x {{ units }} kr
        </dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    data: function() {
        return {
            rate_choices: [
                {id: 1,name: 'Takst 1'},
                {id: 2,name: 'Takst 2'},
                {id: 3,name: 'Takst 3'}
            ]
        }
    },
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
        }
    },
    created: function() {
        this.property = 'payment_rate'
    }

}
</script>