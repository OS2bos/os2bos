<template>
        <div>
          <hr>
          <h2>Betales til</h2>
            <label>Betalingsmodtager</label>
              <select  v-model="selection">
                <option value="INTERNAL">Intern</option>
                <option value="COMPANY">Firma</option>
                <option value="PERSON">Person</option>
              </select>
              <fieldset v-if="selection">
                  <label v-if="selection === 'INTERNAL'" for="field-payee-id">
                    Reference
                  </label>
                  <label v-if="selection === 'COMPANY'" for="field-payee-id">
                    CVR-nr
                  </label>
                  <label v-if="selection === 'PERSON'" for="field-payee-id">
                    CPR-nr
                  </label>
                  <input type="text" id="field-payee-id">
              </fieldset>
              <fieldset>
                  <label for="field-payee-name">Navn</label>
                  <input type="text" id="field-payee-name">
              </fieldset>
        </div>
</template>

<script>
    export default {

      data: function() {
        return {
            selection: null
        }
      }

    }
</script>