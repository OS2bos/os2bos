<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="payment-amount">
        <h1>Betaling</h1>
        <div class="row">
            <fieldset style="margin-right: 2rem;">
                <legend>Hvordan skal det betales?</legend>
                <input type="radio" value="ONE_TIME_PAYMENT" name="pay-type" id="pay-type-1" v-model="entry.payment_type">
                <label for="pay-type-1">Engangsudgift</label>
                <input type="radio" value="RUNNING_PAYMENT" name="pay-type" id="pay-type-2" v-model="entry.payment_type">
                <label for="pay-type-2">Fast beløb, løbende</label>
                <input type="radio" value="PER_HOUR_PAYMENT" name="pay-type" id="pay-type-3" v-model="entry.payment_type">
                <label for="pay-type-3">Pr. time</label>
                <input type="radio" value="PER_DAY_PAYMENT" name="pay-type" id="pay-type-4" v-model="entry.payment_type">
                <label for="pay-type-4">Pr. døgn</label>
                <input type="radio" value="PER_KM_PAYMENT" name="pay-type" id="pay-type-5" v-model="entry.payment_type">
                <label for="pay-type-5">Pr. kilometer</label>
            </fieldset>
            <div>
                <div class="payment-amount-fields">
                    <fieldset v-if="entry.payment_type === 'ONE_TIME_PAYMENT' || entry.payment_type === 'RUNNING_PAYMENT'">
                        <label>Beløb</label>
                        <input v-model="entry.payment_amount" type="number" step="0.01"> kr
                    </fieldset>
                    <fieldset v-if="entry.payment_type && entry.payment_type !== 'ONE_TIME_PAYMENT'">
                        <label for="pay-freq">Hver</label>
                        <select v-model="entry.payment_frequency" id="pay-freq">
                            <option v-for="o in choices.frequency_options" :key="o.key" :value="o.key">
                                {{ o.val }}
                            </option>
                        </select>
                    </fieldset>
                    <fieldset v-if="entry.payment_type === 'PER_HOUR_PAYMENT' || entry.payment_type === 'PER_DAY_PAYMENT' || entry.payment_type === 'PER_KM_PAYMENT'" class="rows">
                        <div style="margin-right: .5rem;">
                            <label v-if="entry.payment_type === 'PER_HOUR_PAYMENT'">betales antal timer</label>
                            <label v-if="entry.payment_type === 'PER_DAY_PAYMENT'">betales antal døgn</label>
                            <label v-if="entry.payment_type === 'PER_KM_PAYMENT'">betales antal kilometer</label>
                            <input v-model="entry.payment_units" type="number">
                        </div>
                        <div>
                            <label>til takst</label>
                            <input v-model="entry.payment_amount" type="number" step="0.01"> kr<br>
                            <a href="https://www.kl.dk/media/16653/taksttabel_-2019.pdf" target="_blank">Find takster her</a>
                        </div>
                    </fieldset>
                </div>
                <payment-plan v-if="entry.payment_amount" :amount="entry.payment_amount" :units="entry.payment_units" :type="entry.payment_type" :frequency="entry.payment_frequency" />
            </div>
        </div>
    </section>

</template>

<script>

    import PaymentPlan from './PaymentPlan.vue'

    export default {

        components: {
            PaymentPlan
        },
        props: [
            'paymentObj'
        ],
        data: function() {
            return {
                choices: {
                    frequency_options: [
                        {
                            key: 'MONTHLY',
                            val: 'Måned'
                        },
                        {
                            key: 'WEEKLY',
                            val: 'Uge'
                        },
                        {
                            key: 'DAILY',
                            val: 'Dag'
                        },
                    ],
                },
                entry: {
                    payment_type: 'RUNNING_PAYMENT', // default is running payment
                    payment_frequency: 'MONTHLY', // default is pr month
                    payment_units: 0,
                    payment_amount: 0
                }
            }
        },
        watch: {
            paymentObj: function() {
                this.entry = this.paymentObj
            },
            entry: {
                handler (newVal) {
                    this.$emit('update', this.entry)
                },
                deep: true
            }
        },
        created: function() {
            if (this.paymentObj) {
                this.entry = this.paymentObj
            }
        }

    }
    
</script>

<style>

    .payment-amount h1 {
        font-size: 1.25rem;
    }

    .payment-amount .payment-amount-fields {
        display: flex;
        flex-flow: row nowrap;
    }

    .payment-amount .payment-amount-fields > fieldset {
        margin: 0 2rem 0 0;
    }

    .payment-amount .payment-plan {
        background-color: var(--grey2);
        padding: 1rem;
    }

    .payment-amount.rows,
    .payment-amount .rows {
        display: flex;
        flex-flow: row nowrap;
    }

    .payment-amount input[type="text"] {
        width: 8rem;
    }

    .payment-schedule-btn {
        margin-left: 1rem;
    }

</style>