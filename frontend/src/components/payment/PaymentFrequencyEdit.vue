<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-frequencies" v-if="p.payment_type && p.payment_type !== 'ONE_TIME_PAYMENT'">

        <label class="required" for="pay-freq">Hver</label>
        <select v-model="p.payment_frequency" id="pay-freq" required>
            <option v-for="o in choices.frequency_options" :key="o.key" :value="o.key">
                {{ o.val }}
            </option>
        </select>
        <error err-key="payment_frequency" />

        <template v-if="p.payment_frequency === 'MONTHLY'">
            <label class="required" for="pay-day-of-month">Betalingsdag d.</label>
            <select v-model="p.payment_day_of_month" id="pay-day-of-month" required>
                <option v-for="o in choices.date_options" :value="o" :key="o">
                    {{ o }}.
                </option>
            </select>
        </template>
        <error err-key="payment_day_of_month" />

    </fieldset>

</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        props: [
            'pay'
        ],
        data: function() {
            return {
                p: {
                    payment_frequency: 'RUNNING_PAYMENT' // default is running payment
                },
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
        watch: {
            pay: function() {
                this.p = this.pay
            },
            p: {
                handler (newVal) {
                    this.$emit('update:pay', this.p)
                },
                deep: true
            }
        },
        created: function() {
            if (this.pay) {
                this.p = this.pay
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