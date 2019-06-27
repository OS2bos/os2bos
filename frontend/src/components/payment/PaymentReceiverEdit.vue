<template>
  <div>
    <hr>
    <h2>Betales til</h2>
    <label>Betalingsmodtager</label>
    <select  v-model="entry.recipient_type">
      <option value="INTERNAL">Intern</option>
      <option value="COMPANY">Firma</option>
      <option value="PERSON">Person</option>
    </select>
    <fieldset v-if="entry.recipient_type">
        <label v-if="entry.recipient_type === 'INTERNAL'" for="field-payee-id">
          Reference
        </label>
        <label v-if="entry.recipient_type === 'COMPANY'" for="field-payee-id">
          CVR-nr
        </label>
        <label v-if="entry.recipient_type === 'PERSON'" for="field-payee-id">
          CPR-nr
        </label>
        <input type="text" id="field-payee-id" v-model="entry.recipient_id">
    </fieldset>
    <fieldset>
        <label for="field-payee-name">Navn</label>
        <input type="text" id="field-payee-name" v-model="entry.recipient_name">
    </fieldset>
  </div>
</template>

<script>
  export default {

    props: [
      'paymentObj'
    ],
    data: function() {
      return {
        entry: {
          recipient_type: null,
          recipient_id: null,
          recipient_name: null
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