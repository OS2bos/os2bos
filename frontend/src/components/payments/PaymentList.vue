<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="payment_schedule">

        <label for="field-year-picker">Vis betalinger fra år</label>
        <select id="field-year-picker" v-model="current_year">
            <option v-for="y in years" :value="y" :key="y.id">{{ y }}</option>
        </select>
        
        <table>
            <thead>
                <tr>
                    <th>Betaling nr</th>
                    <th>Betalingsdato</th>
                    <th>Betalt</th>
                    <th class="right">Beløb</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="p in payments_by_year" :key="p.id">
                    <td>
                        <payment-modal :p-id="p.id" @update="update()"/>
                    </td>
                    <td>
                        <span v-if="p.paid_date">{{ displayDate(p.paid_date) }}<br></span>
                        <span class="dim" style="white-space: nowrap;">{{ displayDate(p.date) }}</span>
                    </td>
                    <td>
                        <span v-if="p.paid === true"><i class="material-icons">check</i></span>
                        <span v-else>-</span>
                    </td>
                    <td class="right">
                        <span v-if="p.paid_amount">{{ displayDigits(p.paid_amount) }} kr.<br></span>
                        <span class="dim" style="white-space: nowrap;">{{ displayDigits(p.amount) }} kr.</span>
                    </td>
                </tr>
                <tr>
                    <th colspan="3" class="right dim">I alt pr valgte år</th>
                    <th class="right dim">{{ displayDigits(sum) }} kr.</th>
                </tr>
            </tbody>
        </table>

    </section>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import PaymentModal from './PaymentModal.vue'

    export default {

        components: {
            PaymentModal
        },
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
                        if (payment.paid_amount) {
                            return total += parseFloat(payment.paid_amount)
                        } else {
                            return total += parseFloat(payment.amount)
                        }
                    }, 0)
                }
            }
        },
        methods: {
            update: function() {
                // Do something to update list of payments
            },
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
        margin: 2rem 0;
    }

    .payment_schedule-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: flex-start;
        align-items: center;
    }

</style>
