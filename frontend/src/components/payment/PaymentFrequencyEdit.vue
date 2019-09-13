<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-frequencies">

        <error err-key="payment_frequency" />

        <!-- <template v-if="entry.payment_type && entry.payment_type !== 'ONE_TIME_PAYMENT'"> -->
        <label class="required" for="pay-freq">Hver</label>
        <select v-model="p.payment_frequency" id="pay-freq" required>
            <option v-for="o in choices.frequency_options" :key="o.key" :value="o.key">
                {{ o.val }}
            </option>
        </select>

        <!-- TODO: insert picker for payment date if monthly -->

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