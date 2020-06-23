<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="payment-plan">
        <h3 class="payment-plan-header">Udgift:</h3>
        <p>{{ summary }} {{ subtotal }} kr {{ freq_name }} </p>
        <p>Årligt <strong>ca. {{ displayCost(total) }} kr</strong></p> 
    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import { rateId2details } from '../filters/Labels.js'

    export default {

        data: function() {
            return {
                summary: null
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPaymentPlan
            },
            rates: function() {
                return this.$store.getters.getRates
            },
            freq_factor: function() {
                switch(this.payment.payment_frequency) {
                    case 'MONTHLY':
                        return 12
                        break
                    case 'BIWEEKLY':
                        return 26
                        break
                    case 'WEEKLY':
                        return 52
                        break
                    case 'DAILY':
                        return 365
                        break
                    default:
                        return 1
                }
            },
            total: function() {
                if (this.subtotal && this.freq_factor) {
                    return this.subtotal * this.freq_factor
                } else {
                    return 0
                }
            },
            subtotal: function() {
                let cost_type = this.payment.payment_cost_type,
                    price_per_unit = this.payment.price_per_unit,
                    units = this.payment.payment_units,
                    rate = this.payment.payment_rate,
                    amount = this.payment.payment_amount

                if (cost_type === 'GLOBAL_RATE') {
                    if (rate) {
                        this.summary = `${ rateId2details(rate).rates_per_date[0].rate } kr x ${ units } =`
                        return rateId2details(rate).rates_per_date[0].rate * units
                    } else {
                        return null
                    }
                } else if (cost_type === 'PER_UNIT') {
                    if (price_per_unit && units) {
                        this.summary = `${ price_per_unit.amount } kr x ${ units } =`
                        return parseInt(price_per_unit.amount) * parseInt(units)
                    } else {
                        return null
                    }
                } else {
                    this.summary = null
                    return amount
                }
            },
            freq_name: function() {
                switch(this.payment.payment_frequency) {
                    case 'MONTHLY':
                        return 'månedligt'
                        break
                    case 'BIWEEKLY':
                        return 'hver 14. dag'
                        break
                    case 'WEEKLY':
                        return 'ugentligt'
                        break
                    case 'DAILY':
                        return 'dagligt'
                        break
                    default:
                        return ''
                }
            }
        },
        methods: {
            displayCost: function(cost) {
                let new_cost = this.roundNum(cost)
                return new Intl.NumberFormat(['da', 'en'], {maximumFractionDigits: 0, minimumFractionDigits: 0} ).format(new_cost)
            },
            roundNum: function(num) {
                //If cost is more than 100, round up cost to nearest hundred
                if (num > 100) {
                    let new_num = num / 100
                    new_num = Math.floor(new_num)
                    return new_num * 100
                } else {
                    return num
                }
            }
        }
    }
    
</script>

<style>

    .payment-plan {
        max-width: 100%;
        padding: .5rem 1rem;
        border: solid .125rem var(--warning);
    }

    .payment-plan-header {
        padding: 0.25rem 0;
    }

</style>