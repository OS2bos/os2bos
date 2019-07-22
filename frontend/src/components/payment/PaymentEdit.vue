<template>
    <section class="payment-method">
        <label>Betalingsmåde</label>
        <select  v-model="entry.payment_method">
            <option value="INVOICE">Faktura</option>
            <option value="INTERNAL">Intern afregning</option>
            <option value="CASH">Betaling</option>
            <option value="SD">SD-løn</option>
        </select>
        <div v-if="entry.payment_method">
            <div v-if="entry.payment_method === 'CASH'">
                <strong>Kontant udbetaling</strong>
                <p>
                Vær opmærksom på at beløbet udbetales til modtagerens Nem-konto. <br>
                Det er ikke muligt at udbetale til et kontonummer.
                </p>
            </div>
            <div v-if="entry.payment_method === 'SD'">
                <strong>Skattekort</strong>
                <input type="radio" id="field-main" name="payment-type" :value="{tax_type: 'MAIN_CARD'}" v-model="entry.payment_method_details">
                <label for="field-main">Hovedkort</label>
                <input type="radio" id="field-secondary" name="payment-type" :value="{tax_type: 'SECONDARY_CARD'}" v-model="entry.payment_method_details">
                <label for="field-secondary">Bikort</label>
            </div>
        </div>
    </section>
</template>

<script>
    export default {

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