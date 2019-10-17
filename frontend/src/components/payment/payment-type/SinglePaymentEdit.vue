<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-type-single">

        <label class="required" for="field-amount-1">Beløb</label>
        <input v-model="p.payment_amount" type="number" step="0.01" required id="field-amount-1"> kr
        
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
                p: {
                    payment_type: 'ONE-TIME-PAYMENT',
                    payment_frequency: null,
                    payment_amount: 0
                }
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        watch: {
            payment: function() {
                this.p = this.payment
            },
            p: {
                handler: function(new_p) {
                    console.log(this.payment)
                    console.log(this.p)
                    console.log(new_p)
                    new_p.payment_type = 'ONE-TIME-PAYMENT'
                    new_p.payment_frequency = null
                    this.$store.commit('setPayment', new_p)
                },
                deep: true
            }
        }

    }
    
</script>