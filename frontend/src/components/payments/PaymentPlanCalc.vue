<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="payment-plan">
        <h3 class="payment-plan-header">Udgift:</h3>
        <p>{{ summary }} {{ displayExactCost(subtotal) }} kr {{ freq_name }} </p>
        <p v-if="total > 0">Årligt ca. <strong>{{ displayCost(total) }} kr</strong></p> 
    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import { rateId2details } from '../filters/Labels.js'
    import { cost2da } from '../filters/Numbers.js'
    import { epoch2DateStr } from '../filters/Date.js'

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
                        this.summary = `${ cost2da(this.getCurrentRate(rateId2details(rate).rates_per_date)) } kr x ${ units } =`
                        return rateId2details(rate).rates_per_date[0].rate * units
                    } else {
                        return null
                    }
                } else if (cost_type === 'PER_UNIT') {
                    if (price_per_unit && units) {
                        this.summary = `${ price_per_unit.amount ? cost2da(price_per_unit.amount) : '-' } kr x ${ units } =`
                        return parseFloat(price_per_unit.amount) * parseFloat(units)
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
            displayExactCost: function(cost) {
                if (cost) {
                    return cost2da(cost)
                } else {
                    return '-'
                }
                
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
            },
            getCurrentRate: function(rates) {
                const now = epoch2DateStr(new Date())
                let live_rates = rates.filter(function(rate) {
                    if (rate.end_date) {
                        if (now >= rate.end_date) {
                            return false
                        } else {
                            return true
                        }
                    } else {
                        return true
                    }
                })
                return live_rates[0].rate
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