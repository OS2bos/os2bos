<template>
    
    <div class="payment">

        <div>
            <h1>Betaling {{ payment.id }}</h1>
            <router-link :to="`/payment/${ payment.id }/edit/`"></router-link>
            <dl>
                <dt>Beløb</dt>
                <dd>{{ payment.amount }} kr</dd>
                <dt>Betalingsdato</dt>
                <dd>{{ payment.date }}</dd>
                <dt>Betalt</dt>
                <dd>{{ payment.paid }}</dd>
            </dl>
        </div>

        <payment-edit />

    </div>

</template>

<script>

    import PaymentEdit from './PaymentEdit.vue'

    export default {
        
        components: {
            PaymentEdit
        },
        computed: {
            p_id: function() {
                return this.$route.params.payId
            },
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        watch: {
            p_id: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchPayment', this.p_id)
            }
        },
        created: function() {
            this.update()
        }

    }

</script>

<style>

    .payment {
        padding: 2rem;
        display: flex;
        flex-flow: row nowrap;
    }

    .payment .payment-edit {
        margin-left: 2rem;
    }

</style>