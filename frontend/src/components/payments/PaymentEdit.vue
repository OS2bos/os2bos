<template>
    
    <div class="payment-edit">
        <form @submit.prevent="">
            <fieldset>
                
                <input type="checkbox" v-model="payment.paid" id="field-paid">
                <label for="field-paid">Betalt</label>
            
                <label for="field-amount">Beløb</label>
                <input type="number" step="0.01" v-model="paid_amount" id="field-amount">
                
                <label for="field-date">Betalingsdato</label>
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

</style>