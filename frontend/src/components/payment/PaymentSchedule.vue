<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="payment_schedule">
        
        <label>Vælg år</label>
        <select v-model="current_year">
            <option v-for="y in years" :value="y" :key="y.id">{{ y }}</option>
        </select>
    
        <table>
            <thead>
                <tr>
                    <th>Dato</th>
                    <th>Beløb</th>
                    <th>Betalt</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="p in payments_by_year" :key="p.id">
                    <td>{{ displayDate(p.date) }}</td>
                    <td>{{ displayDigits(p.amount) }} kr.</td>
                    <td>
                        <span v-if="p.paid === true">Ja</span>
                        <span v-else>Nej</span>
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <th>I alt pr valgte år</th>
                    <th>{{ displayDigits(sum) }} kr.</th>
                </tr>
            </tbody>
        </table>
    </section>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'

    export default {

        props: [
            'payments'
        ],
        data: function() {
            return {
                now: new Date(),
                years: [],
                current_year: null
            }
        },
        computed: {
            payments_by_year: function() {
                if (this.payments) {
                    let payms = this.payments.filter(payment => {
                        return this.current_year === parseInt(payment.date.substr(0,4))
                    })
                    return payms
                } else {
                    return false
                }
                
            },
            sum: function() {
                if (this.payments_by_year) {
                    return this.payments_by_year.reduce(function(total, payment) {
                        return total += parseFloat(payment.amount)
                    }, 0)
                }
            }
        },
        methods: {
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            createYearList: function() {
                this.years.push(this.now.getFullYear() - 1)
                this.years.push(this.now.getFullYear())
                this.years.push(this.now.getFullYear() + 1)
                this.current_year = this.now.getFullYear()
            }
        },
        created: function() {
            this.createYearList()
        }
    }
</script>

<style>

    .payment_schedule {
        margin: 1rem;
    }

    .payment_schedule-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: flex-start;
        align-items: center;
    }

</style>
