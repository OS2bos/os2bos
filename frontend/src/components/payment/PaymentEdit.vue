<template>
        <form @submit.prevent="saveChanges()">
          <h1>Betaling</h1>
            <fieldset>
                <label for="field-cost">Bevilget beløb</label>
                <input type="number" id="field-cost" value="0">
            </fieldset>
            <fieldset>
                <legend>Udgiftstype</legend>
                <input type="radio" id="field-cost-single" :value="false">
                <label for="field-cost-single">Følgeydelse</label>
                <input type="radio" id="field-cost-recurring" :value="true">
                <label for="field-cost-recurring">Enkeltudgift</label>
            </fieldset>
            <fieldset>
                <label for="field-note">Bemærkning</label>
                <textarea id="field-note"></textarea>
            </fieldset>
            <hr>
            <fieldset>
                <legend>Betalingsmodtager</legend>
                <input type="radio" id="field-payment-type-inherit" value="inherit">
                <label for="field-payment-type-inherit">Samme som hovedydelsen</label>
                <input type="radio" id="field-payment-type-intern" value="intern">
                <label for="field-payment-type-intern">Intern</label>
                <input type="radio" id="field-payment-type-person" value="person">
                <label for="field-payment-type-person">Person</label>
                <input type="radio" id="field-payment-type-firm" value="firma">
                <label for="field-payment-type-firm">Firma</label>
            </fieldset>
            <template>
                <fieldset>
                    <label for="field-payment-id">
                        <template>CPR-nr/</template>
                        <template>CVR-nr </template>
                        <template>Reference</template>
                    </label>
                    <input type="text" id="field-payment-id" value="Ukendt">
                </fieldset>
                <fieldset>
                    <label for="field-payment-name">Navn</label>
                    <input type="text" id="field-payment-name" value="Ukendt">
                </fieldset>
                <fieldset>
                    <legend>Betalingsmåde</legend>
                    <input type="radio" id="field-payment-method-cash" value="kontant">
                    <label for="field-payment-method-cash">Kontant udbetaling</label>
                    <input type="radio" id="field-payment-method-sd" value="SD-løn">
                    <label for="field-payment-method-sd">SD-løn</label>
                    <input type="radio" id="field-payment-method-invoice" value="faktura">
                    <label for="field-payment-method-invoice">Faktura</label>
                    <input type="radio" id="field-payment-method-internal" value="intern afregning">
                    <label for="field-payment-method-internal">Intern afregning</label>
                </fieldset>
            </template>
        </form>

</template>

<script>
    export default {

    }
    
</script>