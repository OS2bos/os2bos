<template>
        <div>
          <hr>
          <h2>Betales til</h2>
            <label>Betalingsmodtager</label>
              <select  v-model="entry.selected">
                <option value="INTERNAL">Intern</option>
                <option value="COMPANY">Firma</option>
                <option value="PERSON">Person</option>
              </select>
              <fieldset v-if="entry.selected">
                  <label v-if="entry.selected === 'INTERNAL'" for="field-payee-id">
                    Reference
                  </label>
                  <label v-if="entry.selected === 'COMPANY'" for="field-payee-id">
                    CVR-nr
                  </label>
                  <label v-if="entry.selected === 'PERSON'" for="field-payee-id">
                    CPR-nr
                  </label>
                  <input type="text" id="field-payee-id" v-model="entry.payee_id">
              </fieldset>
              <fieldset>
                  <label for="field-payee-name">Navn</label>
                  <input type="text" id="field-payee-name" v-model="entry.payee_name">
              </fieldset>
        </div>
</template>

<script>
    export default {

      data: function() {
        return {
          entry: {
            selected: null,
            payee_id: null,
            payee_name: null
          }
        }
      },
      watch: {
        entry: {
          handler (newVal) {
            this.$emit('input', newVal)
          },
          deep: true
        }
      }

    }
</script>