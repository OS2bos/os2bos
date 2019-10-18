<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="payment-type-pr-hour">

        <freq-edit />

        <fieldset>

            <div style="margin-right: .5rem;">
                <label class="required" for="field-amount-2">betales antal timer</label>
                <input v-model="p_units" type="number" step="0.01" required id="field-amount-2">
                <error err-key="payment_units" />
            </div>
            <div>
                <label class="required" for="field-rate">til takst</label>
                <input v-model="p_fare" type="number" step="0.01" required id="field-rate"> kr
                <error err-key="payment_amount" />
            </div>

        </fieldset>

    </div>

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
                p_units: null,
                p_fare: null
            }
        },
        computed: {
            units: function() {
                return this.$store.getters.getPaymentUnits
            },
            fare: function() {
                return this.$store.getters.getPaymentAmount
            }
        },
        watch: {
            units: function() {
                this.p_units = this.units
            },
            fare: function() {
                this.p_fare = this.fare
            },
            p_fare: function() {
                this.$store.commit('setPaymentAmount', this.p_fare)
            },
            p_units: function() {
                this.$store.commit('setPaymentUnits', this.p_units)
            }
        },
        created: function() {
            if (this.units) {
                this.p_units = this.units
            }
            if (this.fare) {
                this.p_fare = this.fare
            }
        }

    }
    
</script>