<template>
    <div class="payment-details-wrapper">
        <h3>Betalingshistorik</h3>
        <ol class="payment-details-list">
            <li v-for="ph in payment_history" :key="ph.paid_date">
                <h4>{{ displayTime(ph.history_date) }}</h4>
                <dl>
                    <dt>Betalt</dt>
                    <dd>{{ displayBoolean(ph.paid) }}</dd>
                    <template v-if="ph.paid">
                        <dt>Beløb</dt>
                        <dd>{{ ph.paid_amount }}</dd>
                        <dt>Betalingsdato</dt>
                        <dd>{{ ph.paid_date }}</dd>
                    </template>
                    <dt>Ændret (tid/bruger)</dt>
                    <dd>
                        {{ displayTime(ph.history_date) }}<br>
                        {{ displayUserName(ph.history_user) }}
                    </dd>
                </dl>
            </li>
        </ol>
    </div>
</template>

<script>
import axios from '../http/Http.js'
import { userId2name } from '../filters/Labels.js'

export default {
    props: [
        'payment'
    ],
    data: function() {
        return {
            payment_history: null
        }
    },
    watch: {
        payment: function(new_val, old_val) {
            if (new_val !== old_val) {
                this.update(new_val)
            }
        }
    },
    methods: {
        update: function(p) {
            this.fetchPaymentHistory(p.id)
        },
        fetchPaymentHistory: function(payment_id) {
            axios.get(`/payments/${ payment_id }/history/`)
            .then(res => {
                console.log(res)
                this.payment_history = res.data
            })
            .catch(err => {
                console.log(err)
            })
        },
        displayUserName: function(user_id) {
            return userId2name(user_id)
        },
        displayBoolean: function(boolean) {
            return boolean ? 'Ja' : 'Nej'
        },
        displayTime: function(time) {
            return new Date(time).toLocaleString()
        }
    },
    created: function() {
        this.update(this.payment)
    }
}
</script>

<style>
    .payment-details-list {
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .payment-details-list > li {
        border-top: solid 1px #ddd;
        margin-top: .5rem;
    }

    .payment-details-list h4 {
        margin: 0;
        padding: 1rem 0 0;
        font-weight: bold;
    }
</style>
