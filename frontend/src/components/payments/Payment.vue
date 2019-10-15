<template>
    
    <div class="payment">

        <div>
            <nav class="payment-nav">
                <router-link to="">
                    <i class="material-icons">arrow_upward</i>
                    Ydelse xxx
                </router-link>
            </nav>
            <h1>Betaling #{{ payment.id }}</h1>
            <router-link :to="`/payment/${ payment.id }/edit/`"></router-link>
            <dl>
                <dt>Betalingsnøgle</dt>
                <dd>00023897</dd>
                
                <dt>Beløb, planlagt</dt>
                <dd>{{ payment.amount }} kr</dd>
                <dt>Betalingsdato, planlagt</dt>
                <dd>{{ payment.date }}</dd>
                <dt>Kontostreng</dt>
                <dd>xxxx-2389237-dlihseg-xxx</dd>
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
        margin: 2rem auto;
    }

    .payment .payment-nav {
        background-color: var(--grey1);
    }

    .payment .payment-nav > a {
        border-bottom: none;
        padding: .5rem 1rem;
        display: block;
    }

    .payment .payment-edit {
        margin: 1rem 0 0;
    }

</style>