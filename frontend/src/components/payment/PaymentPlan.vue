<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <article class="payment-plan">
        <h1>Forventet udgift</h1>
        <p>{{ abstract }}</p>
        <p v-if="yearly_cost">Det er <strong>{{ yearly_cost }} kr</strong> pr. år</p>
    </article>

</template>

<script>

    export default {

        props: [
            'amount',
            'units',
            'type',
            'frequency'
        ],
        data: function() {
            return {
                freq_factor: 0,
                month_factor: 0
            }
        },
        computed: {
            abstract: function() {
                let str = 'Udgiften bliver '

                switch(this.type) {
                    case 'ONE_TIME_PAYMENT':
                        str += `${ this.amount } kr én gang`
                        break
                    case 'RUNNING_PAYMENT':
                        str += `${ this.amount } kr hver ${ this.freq_name }`
                        break
                    case 'PER_HOUR_PAYMENT':
                        if (this.units) {
                            str += `${ this.units } timer á ${ this.amount } kr hver ${ this.freq_name }`
                        } else {
                            str = '-'
                        }
                        break
                    case 'PER_DAY_PAYMENT':
                        if (this.units) {
                            str += `${ this.units } døgn á ${ this.amount } kr hver ${ this.freq_name }`
                        } else {
                            str = '-'
                        }
                        break
                    case 'PER_KM_PAYMENT':
                        if (this.units) {
                            str += `${ this.units } kilometer á ${ this.amount } kr hver ${ this.freq_name }`
                        } else {
                            str = '-'
                        }
                        break
                    default:
                        str += 'intet'
                }

                return str
            },
            yearly_cost: function() {
                let num = 0
                switch(this.type) {
                    case 'ONE_TIME_PAYMENT':
                        num = this.amount
                        break
                    case 'RUNNING_PAYMENT':
                        num = this.amount * this.freq_factor
                        break
                    default:
                        num = this.amount * this.freq_factor * this.units
                }
                return num
            },
            freq_name: function() {
                switch(this.frequency) {
                    case 'MONTHLY':
                        this.freq_factor = 12
                        this.month_factor = 1
                        return 'måned'
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
        },
        methods: {

            
        }

    }
    
</script>

<style>

    .payment-plan h1 {
        font-size: 1.25rem;
        padding-top: 0;
    }

</style>