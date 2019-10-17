<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-types">

        <legend class="required" style="margin-bottom: .75rem;">Hvor ofte og hvor meget?</legend>

        <error err-key="payment_type" />

        {{ payment }}

        <input type="radio" value="ONE_TIME_PAYMENT" name="pay-type" id="pay-type-1" v-model="p.payment_type" required>
        <label for="pay-type-1">Engangsudgift</label>
        <input type="radio" value="RUNNING_PAYMENT" name="pay-type" id="pay-type-2" v-model="p.payment_type" required>
        <label for="pay-type-2">Fast beløb, løbende</label>
        <input type="radio" value="PER_HOUR_PAYMENT" name="pay-type" id="pay-type-3" v-model="p.payment_type" required>
        <label for="pay-type-3">Pr. time</label>
        <input type="radio" value="PER_DAY_PAYMENT" name="pay-type" id="pay-type-4" v-model="p.payment_type" required>
        <label for="pay-type-4">Pr. døgn</label>
        <input type="radio" value="PER_KM_PAYMENT" name="pay-type" id="pay-type-5" v-model="p.payment_type" required>
        <label for="pay-type-5">Pr. kilometer</label>

        <p style="margin-top: .75rem;">
            <a href="https://www.kl.dk/media/16653/taksttabel_-2019.pdf" target="_blank">Find takster her</a>
        </p>

    </fieldset>

</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        data: function() {
            return {
                p: {
                    payment_type: 'RUNNING_PAYMENT' // default is running payment
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
                    this.$store.commit('setPayment', new_p)
                },
                deep: true
            }
        },
        created: function() {
            
        }

    }
    
</script>