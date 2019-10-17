<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-frequencies row">

        <div>
            <label class="required" for="pay-freq">Hver</label>
            <select v-model="p_payment_frequency" id="pay-freq" required>
                <option v-for="o in choices.frequency_options" :key="o.key" :value="o.key">
                    {{ o.val }}
                </option>
            </select>
            <error err-key="payment_frequency" />
        </div>

        <div v-if="p_payment_frequency === 'MONTHLY'" style="margin-left: .5rem;">
            <label class="required" for="pay-day-of-month">den</label>
            <select v-model="p_payment_day_of_month" id="pay-day-of-month" required>
                <option v-for="o in choices.date_options" :value="o" :key="o">
                    {{ o }}.
                </option>
            </select>
            <error err-key="payment_day_of_month" />
        </div>
        
    </fieldset>

</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        data: function() {
            return {
                p_payment_frequency: 'MONTHLY', // default is running payment
                p_payment_day_of_month: null,
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
                    date_options: [
                        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27 ,28 ,29, 30, 31
                    ]
                }
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        watch: {
            payment: function() {
                this.p_payment_frequency = this.payment.payment_frequency
                this.p_payment_day_of_month = this.payment.payment_day_of_month
            },
            p_payment_frequency: function() {
                this.$store.commit('setPaymentFreq', this.p_payment_frequency)
            },
            p_payment_day_of_month: function() {
                this.$store.commit('setPaymentDayOfMonth', this.p_payment_day_of_month)
            }
        }

    }
    
</script>

<style>

    .payment-frequencies #pay-freq,
    .payment-frequencies #pay-day-of-month {
        width: auto;
    }

</style>