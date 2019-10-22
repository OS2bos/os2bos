<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <fieldset class="payment-payee-person">

        <div>
            <cpr-lookup :cpr.sync="p_recipient_id" :name.sync="p_recipient_name" />
        </div>

        <label class="required" for="field-pay-method">Betalingsmåde</label>
        <select v-model="p_payment_method" required id="field-pay-method">
            <option value="CASH">Betaling</option>
            <option value="SD">SD-løn</option>
        </select>
        <error err-key="payment_method" />

        <div v-if="p_payment_method" style="margin-top: 1rem;">
            <div v-if="p_payment_method === 'CASH'">
                <p>
                    <strong>Kontant udbetaling</strong>
                </p>
                <p>
                    Vær opmærksom på at beløbet udbetales til modtagerens Nem-konto.<br>
                    Det er ikke muligt at udbetale til et kontonummer.
                </p>
            </div>

            <template v-if="p_payment_method === 'SD'">
                <legend class="required">Skattekort</legend>
                <input type="radio" id="field-main" name="payment-type" value="1" v-model="p_payment_method_details" required>
                <label for="field-main">Hovedkort</label>
                <input type="radio" id="field-secondary" name="payment-type" value="2" v-model="p_payment_method_details" required>
                <label for="field-secondary">Bikort</label>
            </template>

        </div>

    </fieldset>
</template>

<script>

    import Error from '../../forms/Error.vue'
    import CprLookup from '../../forms/CprLookUp.vue'

    export default {

        components: {
            Error,
            CprLookup
        },
        data: function() {
            return {
                p_recipient_id: null,
                p_recipient_name: null,
                p_payment_method: null,
                p_payment_method_details: null
            }
        },
        computed: {
            recipient_id: function() {
                return this.$store.getters.getPaymentRecipientId
            },
            recipient_name: function() {
                return this.$store.getters.getPaymentRecipientName
            },
            method: function() {
                return this.$store.getters.getPaymentMethod
            },
            method_details: function() {
                return this.$store.getters.getPaymentMethodDetails
            }
        },
        watch: {
            recipient_id: function() {
                this.p_recipient_id = this.recipient_id
            },
            recipient_name: function() {
                this.p_recipient_name = this.recipient_name
            },
            method: function() {
                this.p_payment_method = this.method
            },
            method_details: function() {
                this.p_payment_method_details = this.method_details
            },
            p_recipient_id: function() {
                this.$store.commit('setPaymentRecipientId', this.p_recipient_id)
            },
            p_recipient_name: function() {
                this.$store.commit('setPaymentRecipientName', this.p_recipient_name)
            },
            p_payment_method: function() {
                this.$store.commit('setPaymentMethod', this.p_payment_method)
            },
            p_payment_method_details: function() {
                this.$store.commit('setPaymentMethodDetails', this.p_payment_method_details)
            }
        },
        created: function() {
            if (this.recipient_id) {
                this.p_recipient_id = this.recipient_id
            }
            if (this.recipient_name) {
                this.p_recipient_name = this.recipient_name
            }
            if (this.method) {
                this.p_payment_method = this.method
            }
            if (this.method_details) {
                this.p_payment_method_details = this.method_details
            }
        }

    }

</script>