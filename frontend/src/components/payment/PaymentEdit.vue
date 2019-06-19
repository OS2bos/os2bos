<template>
        <div>
          <hr>
          <h2>Betaling</h2>
            <label>Betalingsmåde</label>
            <select  v-model="selection">
              <option value="INVOICE">Faktura</option>
              <option value="INTERNAL">Intern afregning</option>
              <option value="CASH">Kontant udbetaling</option>
              <option value="SD">SD-løn</option>
            </select>
            <div v-if="selection">
                <div v-if="selection === 'CASH'">
                  <h4>Kontant udbetaling</h4>
                  <p>
                    Vær opmærksom på at beløbet udbetales til modtagerens Nem-konto. <br>
                    Det er ikke muligt at udbetale til et kontonummer.
                  </p>
                </div>
                <div v-if="selection === 'SD'">
                  <h4>Skattekort</h4>
                  <input type="radio" id="field-main" name="payment-type" value="MAIN_CARD">
                  <label for="field-main">Hovedkort</label>
                  <input type="radio" id="field-secondary" name="payment-type" value="SECONDARY_CARD">
                  <label for="field-secondary">Bikort</label>
                </div>
            </div>
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