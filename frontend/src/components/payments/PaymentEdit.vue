<template>
    
    <div class="payment-edit">
        <dl>
            <dt>Betalt</dt>
            <dd>
                <span v-if="payment.paid">Ja</span>
                <span v-else>Nej</span>
            </dd>
            <template v-if="payment.paid">
                <dt>Beløb</dt>
                <dd>
                    (Faktisk betalt beløb)
                </dd>
                <dt>Dato</dt>
                <dd>
                    (Faktisk betalingsdato)
                </dd>
            </template>
        </dl>
        <form @submit.prevent="" v-if="!payment.paid">
            <fieldset>
            
                <label for="field-amount">Betal beløb</label>
                <input type="number" step="0.01" v-model="paid_amount" id="field-amount">
                
                <label for="field-date">Betal dato</label>
                <input type="date" v-model="paid_date" id="field-date">
                
            </fieldset>
        </form>

    </div>

</template>

<script>

    export default {
        
        data: function() {
            return {
                paid_amount: null,
                paid_date: null
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPayment
            }
        }

    }

</script>

<style>

    .payment-edit {
        padding: 1rem 2rem;
        background-color: var(--grey1);
    }

    .payment-edit form {
        padding: 0;
    }

</style>