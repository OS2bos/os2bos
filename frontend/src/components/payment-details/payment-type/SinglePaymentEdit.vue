<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-type-single">

        <label class="required" for="field-amount-1">Beløb</label>
        <input v-model="p_amount" type="number" step="0.01" required id="field-amount-1"> kr
        <error err-key="payment_amount" />

    </fieldset>

</template>

<script>

    import Error from '../../forms/Error.vue'

    export default {

        components: {
            Error
        },
        data: function() {
            return {
                p_amount: 0 // default is 0
            }
        },
        computed: {
            amount: function() {
                return this.$store.getters.getPaymentAmount
            }
        },
        watch: {
            payment: function() {
                this.p_amount = this.amount
            },
            p_amount: function() {
                this.$store.commit('setPaymentFreq', null)
                this.$store.commit('setPaymentAmount', this.p_amount)
            }
        },
        created: function() {
            if (this.amount) {
                this.p_amount = this.amount
            }
        }

    }
    
</script>