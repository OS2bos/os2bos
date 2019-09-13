<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="payment-amount row">
        <fieldset class="payment-amount-types">
            <legend class="required" style="margin-bottom: .75rem;">Hvordan skal det betales?</legend>
            <input type="radio" value="ONE_TIME_PAYMENT" name="pay-type" id="pay-type-1" v-model="entry.payment_type" required>
            <label for="pay-type-1">Engangsudgift</label>
            <input type="radio" value="RUNNING_PAYMENT" name="pay-type" id="pay-type-2" v-model="entry.payment_type" required>
            <label for="pay-type-2">Fast beløb, løbende</label>
            <input type="radio" value="PER_HOUR_PAYMENT" name="pay-type" id="pay-type-3" v-model="entry.payment_type" required>
            <label for="pay-type-3">Pr. time</label>
            <input type="radio" value="PER_DAY_PAYMENT" name="pay-type" id="pay-type-4" v-model="entry.payment_type" required>
            <label for="pay-type-4">Pr. døgn</label>
            <input type="radio" value="PER_KM_PAYMENT" name="pay-type" id="pay-type-5" v-model="entry.payment_type" required>
            <label for="pay-type-5">Pr. kilometer</label>
            <error err-key="payment_type" />
        </fieldset>
        
        <fieldset class="payment-amount-fields">
            <template v-if="entry.payment_type === 'ONE_TIME_PAYMENT' || entry.payment_type === 'RUNNING_PAYMENT'">
                <label class="required" for="field-amount-1">Beløb</label>
                <input v-model="entry.payment_amount" type="number" step="0.01" required id="field-amount-1"> kr
                <error err-key="payment_amount" />
            </template>
            <template v-if="entry.payment_type && entry.payment_type !== 'ONE_TIME_PAYMENT'">
                <label class="required" for="pay-freq">Hver</label>
                <select v-model="entry.payment_frequency" id="pay-freq" required>
                    <option v-for="o in choices.frequency_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
            </template>
            <template v-if="entry.payment_type === 'PER_HOUR_PAYMENT' || entry.payment_type === 'PER_DAY_PAYMENT' || entry.payment_type === 'PER_KM_PAYMENT'" class="rows">
                <div style="margin-right: .5rem;">
                    <label class="required" for="field-amount-2" v-if="entry.payment_type === 'PER_HOUR_PAYMENT'">betales antal timer</label>
                    <label class="required" for="field-amount-2" v-if="entry.payment_type === 'PER_DAY_PAYMENT'">betales antal døgn</label>
                    <label class="required" for="field-amount-2" v-if="entry.payment_type === 'PER_KM_PAYMENT'">betales antal kilometer</label>
                    <input v-model="entry.payment_units" type="number" required id="field-amount-2">
                    <error err-key="payment_units" />
                </div>
                <div>
                    <label class="required" for="field-rate">til takst</label>
                    <input v-model="entry.payment_amount" type="number" step="0.01" required id="field-rate"> kr
                    <error err-key="payment_amount" />
                </div>
                <p style="margin-top: .75rem;">
                    <a href="https://www.kl.dk/media/16653/taksttabel_-2019.pdf" target="_blank">Find takster her</a>
                </p>
            </template>
        </fieldset>
        <div class="payment-amount-plan">
            <payment-plan v-if="entry.payment_amount" :amount="entry.payment_amount" :units="entry.payment_units" :type="entry.payment_type" :frequency="entry.payment_frequency" />
        </div>
    </section>

</template>

<script>

    import PaymentPlan from './PaymentPlan.vue'
    import Error from '../forms/Error.vue'

    export default {

        components: {
            PaymentPlan,
            Error
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
                            key: 'BIWEEKLY',
                            val: '2. uge'
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

    .payment-amount {
        padding: 0 1rem 1rem;
    }

    .payment-amount .payment-amount-types,
    .payment-amount .payment-amount-fields,
    .payment-amount .payment-amount-plan {
        margin: 1rem;
    }

    .payment-amount .payment-plan {
        border: solid .25rem hsl(40, 90%, 70%);
        background-color: hsl(40, 90%, 80%);
    }

</style>