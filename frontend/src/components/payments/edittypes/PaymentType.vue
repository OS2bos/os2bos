<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div>
        <fieldset v-if="editable && !act.modifies">
            <legend class="required">Afregning</legend>
            <input 
                type="radio" 
                v-model="model" 
                id="pay-type-running" 
                value="RUNNING_PAYMENT">
            <label for="pay-type-running">Løbende ydelse</label>
            <input 
                type="radio" 
                v-model="model" 
                id="pay-type-single" 
                value="ONE_TIME_PAYMENT">
            <label for="pay-type-single">Engangsudgift</label>
            <input 
                type="radio" 
                v-model="model" 
                id="pay-type-individual" 
                value="INDIVIDUAL_PAYMENT">
            <label for="pay-type-individual">Individuel betalingsplan</label>
            <error :err-key="property" />
        </fieldset>
        
        <dl v-else>
            <dt>Afregning</dt>
            <dd>{{ dispPayType(model) }}</dd>
        </dl>

        <p v-if="model === 'INDIVIDUAL_PAYMENT'">
            Ved individuel betalingsplan opretter du betalinger ved at gå til "Betalinger" for denne ydelse og vælge <strong>"Tilføj betaling"</strong>
        </p>
    </div>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue'
import { displayPayType } from '../../filters/Labels.js'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    computed: {
        act: function() {
            return this.$store.getters.getActivity
        }
    },
    watch: {
        model: function(new_val) {

            /****** RULES ******/ 
            
            // If one time payment or individual, reset payment frequency and end date
            if (new_val === 'ONE_TIME_PAYMENT' || new_val === 'INDIVIDUAL_PAYMENT') {
                this.$store.commit('setPaymentPlanProperty',{
                    prop: 'end_date', 
                    val: null
                })
                this.$store.commit('setPaymentPlanProperty',{
                    prop: 'payment_frequency', 
                    val: null
                })
                this.$store.commit('removePaymentPlanProperty', 'payment_day_of_month')
            }
        }
    },
    methods: {
        dispPayType: function(type) {
            return displayPayType(type)
        }
    },
    created: function() {
        this.property = 'payment_type'
    }
}
</script>