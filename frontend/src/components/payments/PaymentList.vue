<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section class="payment_schedule">

        <fieldset class="payment-schedule-selector">
            <label for="field-year-picker">Vis betalinger fra år</label>
            <select id="field-year-picker" v-model="current_year">
                <option v-for="y in years" :value="y" :key="y.id">{{ y }}</option>
            </select>
        </fieldset>
        
        <table v-if="payments_by_year.length > 0">
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
                        <span class="dim" v-if="p.payment_schedule__fictive">(Fiktiv)</span>
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
                    <td class="right dim">{{ displayDigits(sum) }} kr.</td>
                </tr>
            </tbody>
        </table>

        <p v-else style="margin-top: 2rem;">Der er ingen betalinger for det valgte år</p>

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
            'pId'
        ],
        data: function() {
            return {
                now: new Date(),
                years: [],
                current_year: null
            }
        },
        computed: {
            payments: function() {
                return this.$store.getters.getPaymentPlan.payments
            },
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
                this.$store.dispatch('fetchPaymentPlan', this.pId)
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

    .payment-schedule-selector {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        margin: 1rem 0 0;
    }

    .payment-schedule-selector label {
        margin: 0 .5rem 0 0;
    }

</style>
