<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-type-pr-day">

        <freq-edit />

        <div style="margin-right: .5rem;">
            <label class="required" for="field-amount-2">Antal Døgn</label>
            <input v-model="p.payment_units" type="number" step="0.01" required id="field-amount-2">
            <error err-key="payment_units" />
        </div>
        <div>
            <label class="required" for="field-rate">Takst</label>
            <input v-model="p.payment_amount" type="number" step="0.01" required id="field-rate"> kr
            <error err-key="payment_amount" />
        </div>

    </fieldset>

</template>

<script>

    import Error from '../../forms/Error.vue'
    import FreqEdit from '../PaymentFrequencyEdit.vue'

    export default {

        components: {
            Error,
            FreqEdit
        },
        data: function() {
            return {
                p: null
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
        }

    }
    
</script>