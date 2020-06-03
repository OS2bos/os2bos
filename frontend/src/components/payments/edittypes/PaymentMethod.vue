<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
                
    <fieldset v-if="editable">
        <legend class="required">Betalingsmåde</legend>

        <input 
            type="radio" 
            id="pay-method-sd"
            v-model="model"
            value="SD"
            name="pay-method"
            required>
        <label for="pay-method-sd">SD-Løn</label>

        <input 
            type="radio" 
            id="pay-method-cash"
            v-model="model"
            value="CASH"
            name="pay-method"
            required>
        <label for="pay-method-cash">Udbetaling</label>

        <!--
        <input 
            type="radio" 
            id="pay-method-internal"
            v-model="model"
            value="INTERNAL"
            name="pay-method"
            required>
        <label for="pay-method-internal">Intern</label>

        <input 
            type="radio" 
            id="pay-method-invoice"
            v-model="model"
            value="INVOICE"
            name="pay-method"
            required>
        <label for="pay-method-invoice">Faktura</label>
        -->

        <div v-if="model === 'CASH'">
            <p>
                <strong>Kontant udbetaling</strong>
            </p>
            <p>
                Vær opmærksom på at beløbet udbetales til modtagerens Nem-konto.<br>
                Det er ikke muligt at udbetale til et kontonummer.
            </p>
        </div>

        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Betalingsmåde</dt>
        <dd>{{ dispPayMethod(model) }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue' 
import { displayPayMethod } from '../../filters/Labels.js'

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
            
            // If method type is not SD, reset payment method details
            if (new_val !== 'SD') {
                this.$store.commit('setPaymentPlanProperty', {
                    prop: 'payment_method_details',
                    val: null
                })
            }
        }
    },
    methods: {
        dispPayMethod: function(method) {
            return displayPayMethod(method)
        }
    },
    created: function() {
        this.property = 'payment_method'
    }
}    
</script>
