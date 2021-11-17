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
                value="RUNNING_PAYMENT"
                @change="resetValues">
            <label for="pay-type-running">Løbende ydelse</label>
            <template v-if="act && act.activity_type !== 'MAIN_ACTIVITY'">
                <input
                    type="radio"
                    v-model="model"
                    id="pay-type-single"
                    value="ONE_TIME_PAYMENT"
                    @change="resetValues">
                <label for="pay-type-single">Engangsudgift</label>
            </template>
            <input 
                type="radio" 
                v-model="model" 
                id="pay-type-individual" 
                value="INDIVIDUAL_PAYMENT"
                @change="resetValues">
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
    methods: {
        dispPayType: function(type) {
            return displayPayType(type)
        },
        resetValues: function() {
            this.$store.commit('setPaymentPlanProperty',{
                prop: 'start_date', 
                val: null
            })
            this.$store.commit('setPaymentPlanProperty',{
                prop: 'end_date', 
                val: null
            })
            this.$store.commit('setPaymentPlanProperty',{
                prop: 'payment_frequency', 
                val: null
            })
            if (this.model === 'ONE_TIME_PAYMENT') {
                // Remove all data for price for unit because they do not apply to one time payments
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'payment_cost_type',
                    val: null
                })
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'price_per_unit',
                    val: null
                })
                this.$store.commit('setPaymentPlanProperty', {
                    prop: 'payment_units',
                    val: null
                })
            }
        }
    },
    created: function() {
        this.property = 'payment_type'
    }
}
</script>