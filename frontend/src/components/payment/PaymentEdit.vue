<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="payment-method">
        <label class="required">Betalingsmåde</label>
        <select v-model="entry.payment_method" required>
            <option value="INVOICE" v-if="paymentObj.recipient_type === 'COMPANY'">Faktura</option>
            <option value="INTERNAL" v-if="paymentObj.recipient_type === 'INTERNAL'">Intern afregning</option>
            <option value="CASH" v-if="paymentObj.recipient_type === 'PERSON' || paymentObj.recipient_type === 'COMPANY'">
              Betaling
            </option>
            <option value="SD" v-if="paymentObj.recipient_type === 'PERSON'">SD-løn</option>
        </select>
        <error err-key="payment_method" />
        <div v-if="entry.payment_method">
            <div v-if="entry.payment_method === 'CASH'">
                <strong>Kontant udbetaling</strong>
                <p>
                Vær opmærksom på at beløbet udbetales til modtagerens Nem-konto. <br>
                Det er ikke muligt at udbetale til et kontonummer.
                </p>
            </div>
            <fieldset v-if="entry.payment_method === 'SD'">
                <legend class="required">Skattekort</legend>
                <input type="radio" id="field-main" name="payment-type" value="1" v-model="entry.payment_method_details">
                <label for="field-main">Hovedkort</label>
                <input type="radio" id="field-secondary" name="payment-type" value="2" v-model="entry.payment_method_details">
                <label for="field-secondary">Bikort</label>
            </fieldset>
        </div>
    </section>
</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

      components: {
        Error
      },
      props: [
        'paymentObj'
      ],
      data: function() {
        return {
          entry: {
            payment_method: null,
            payment_method_details: null
          }
        }
      },
      watch: {
        paymentObj: function() {
          this.entry = this.paymentObj
        },
        entry: {
          handler (newVal) {
            this.$emit('update', this.entry)
          },
          deep: true
        }
      },
      created: function() {
        if (this.paymentObj) {
          this.entry = this.paymentObj
        }
      }
    }
</script>

<style>

    .payment-method {
        margin: 1rem 0;
    }

</style>