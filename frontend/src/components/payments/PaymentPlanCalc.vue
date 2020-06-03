<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="payment-plan">
        <p style="font-size: 1.5rem;">Forventet udgift</p>
        <p>{{ abstract }}</p>
        <p v-if="yearly_cost">Det er ca. <strong>{{ yearly_cost }} kr.</strong> pr. år</p>
    </div>

</template>

<script>

    import { cost2da } from '../filters/Numbers.js'

    export default {

        data: function() {
            return {
                freq_factor: 0,
                month_factor: 0
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPaymentPlan
            },
            abstract: function() {
                let str = 'Udgiften bliver '

                if (this.payment.payment_cost_type === 'RATE') {
                    // TODO TODO
                }

                switch(this.payment.payment_type) {
                    case 'ONE_TIME_PAYMENT':
                        str += `${ cost2da(this.payment.payment_amount) }`
                        break
                    case 'RUNNING_PAYMENT':
                        str += `${ cost2da(this.payment.payment_amount) } kr hver ${ this.freq_name }`
                        break
                    default:
                        str += 'intet'
                }

                return str
            },
            yearly_cost: function() {
                let num = 0
                switch(this.payment.payment_type) {
                    case 'ONE_TIME_PAYMENT':
                        num = this.payment.payment_amount
                        break
                    case 'RUNNING_PAYMENT':
                        num = this.payment.payment_amount * this.freq_factor
                        break
                    default:
                        num = this.payment.payment_amount * this.freq_factor * this.payment.payment_units
                }
                return cost2da(num)
            },
            freq_name: function() {
                switch(this.payment.payment_frequency) {
                    case 'MONTHLY':
                        this.freq_factor = 12
                        this.month_factor = 1
                        return 'måned'
                        break
                    case 'BIWEEKLY':
                        this.freq_factor = 26
                        this.month_factor = 2
                        return '2. uge'
                        break
                    case 'WEEKLY':
                        this.freq_factor = 52
                        this.month_factor = 4
                        return 'uge'
                        break
                    case 'DAILY':
                        this.freq_factor = 365
                        this.month_factor = 31
                        return 'dag'
                        break
                    default:
                        return '-'
                }
            }
        }

    }
    
</script>

<style>

    .payment-plan {
        white-space: nowrap;
        padding: 1rem 2rem;
    }

    .payment-plan h3 {
        font-size: 1.25rem;
        padding-top: .25rem;
    }

</style>