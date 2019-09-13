<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-means">

        <legend>Hvordan skal det betales?</legend>
        <label class="required" for="field-pay-method">Betalingsmåde</label>
        <select v-model="p.payment_method" required id="field-pay-method">
            <option value="INVOICE" v-if="p.recipient_type === 'COMPANY'">Faktura</option>
            <option value="INTERNAL" v-if="p.recipient_type === 'INTERNAL'">Intern afregning</option>
            <option value="CASH" v-if="p.recipient_type === 'PERSON' || p.recipient_type === 'COMPANY'">
              Betaling
            </option>
            <option value="SD" v-if="p.recipient_type === 'PERSON'">SD-løn</option>
        </select>
        <error err-key="payment_method" />
        <div v-if="p.payment_method" style="margin-top: 1rem;">
            <div v-if="p.payment_method === 'CASH'">
                <p>
                    <strong>Kontant udbetaling</strong>
                </p>
                <p>
                Vær opmærksom på at beløbet udbetales til modtagerens Nem-konto. <br>
                Det er ikke muligt at udbetale til et kontonummer.
                </p>
            </div>

            <template v-if="p.payment_method === 'SD'">
                <legend class="required">Skattekort</legend>
                <input type="radio" id="field-main" name="payment-type" value="1" v-model="p.payment_method_details">
                <label for="field-main">Hovedkort</label>
                <input type="radio" id="field-secondary" name="payment-type" value="2" v-model="p.payment_method_details">
                <label for="field-secondary">Bikort</label>
            </template>

        </div>
    </fieldset>

</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        props: [
            'pay'
        ],
        data: function() {
            return {
                p: {
                    payment_method: null,
                    payment_method_details: null
                }
            }
        },
        watch: {
            pay: function() {
                this.p = this.pay
            },
            p: {
                handler (newVal) {
                    this.$emit('update', this.p)
                },
                deep: true
            }
        },
        created: function() {
            if (this.pay) {
                this.p = this.pay
            }
        }
    }
</script>