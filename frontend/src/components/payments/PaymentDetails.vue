<template>
    
    <table class="payment-details-list">
        <thead>
            <tr>
                <th>Ændret/oprettet</th>
                <th style="text-align: center; width: 4.5rem;">Betalt</th>
                <th style="text-align: right;">Beløb</th>
                <th style="width: 8rem;">Betalingsdato</th>
                <th>Bruger</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="ph in payment_history" :key="ph.paid_date">
                <td>{{ displayTime(ph.history_date) }}</td>
                <td style="text-align: center; width: 4.5rem;">{{ displayBoolean(ph.paid) }}</td>
                <td style="text-align: right;">{{ displayCost(ph.paid_amount) }}</td>
                <td style="width: 8rem;">{{ displayDate(ph.paid_date) }}</td>
                <td>{{ displayUserName(ph.history_user) }}</td>
            </tr>
        </tbody>
    </table>

</template>

<script>
import axios from '../http/Http.js'
import { userId2name } from '../filters/Labels.js'
import { json2jsDate } from '../filters/Date.js'
import { cost2da } from '../filters/Numbers.js'

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
        },
        displayDate: function(date) {
            return json2jsDate(date)
        },
        displayCost: function(cost) {
            return cost2da(cost)
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
        table-layout: auto;
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
