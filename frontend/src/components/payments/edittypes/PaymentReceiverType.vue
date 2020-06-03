<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
                
    <fieldset v-if="editable">
        <legend class="required">Modtagertype</legend>

        <input 
            type="radio" 
            id="pay-receiver-type-internal" 
            v-model="model" 
            name="pay-receiver-type"
            value="INTERNAL"
            required>
        <label for="pay-receiver-type-internal">Intern</label>

        <input 
            type="radio" 
            id="pay-receiver-type-company" 
            v-model="model" 
            name="pay-receiver-type"
            value="COMPANY"
            required>
        <label for="pay-receiver-type-company">Firma</label>

        <input 
            type="radio" 
            id="pay-receiver-type-person" 
            v-model="model" 
            name="pay-receiver-type"
            value="PERSON"
            required>
        <label for="pay-receiver-type-person">Person</label>

        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Betalingsmodtager</dt>
        <dd>{{ dispPayReceiverType(model) }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue' 
import { displayPayReceiverType } from '../../filters/Labels.js'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    watch: {
        model: function(new_val) {

            /****** RULES ******/ 
            
            // If receiver type is 'COMPANY', payment method must be 'INVOICE'
            if (new_val === 'COMPANY') {
                this.$store.commit('setPaymentPlanProperty', {
                    prop: 'payment_method',
                    val: 'INVOICE'
                })
            }
            // If receiver type is 'INTERNAL', payment method must be 'INTERNAL'
            if (new_val === 'INTERNAL') {
                this.$store.commit('setPaymentPlanProperty', {
                    prop: 'payment_method',
                    val: 'INTERNAL'
                })
            }
        }
    },
    methods: {
        dispPayReceiverType: function(type) {
            return displayPayReceiverType(type)
        }
    },
    created: function() {
        this.property = 'recipient_type'
    }
}    
</script>
