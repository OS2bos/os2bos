<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div class="payment-search">

        <div class="payment-search-list">
            <h1>Betalinger</h1>
            <template>
                <table v-if="payments.length > 0">
                    <thead>
                        <tr>
                            <th>Betaling nr</th>
                            <th>Betalingsnøgle</th>
                            <th>CPR nr</th>
                            <th>Betalingsdato</th>
                            <th>Betalt</th>
                            <th class="right">Beløb</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in payments" :key="p.id">
                            <template v-if="p.activity__status === 'GRANTED'">
                            <td>
                                <payment-modal :p-id="p.id" @update="update()"/>
                            </td>
                            <td> {{ p.payment_schedule__payment_id }} </td>
                            <td> {{ p.case__cpr_number }} </td>
                            <td>
                                <span v-if="p.paid_date" style="white-space: nowrap;">
                                    {{ displayDate(p.paid_date) }}<br>
                                </span>
                                <span class="dim" style="white-space: nowrap;">
                                    {{ displayDate(p.date) }}
                                </span>
                            </td>
                            <td>
                                <span v-if="p.paid"><i class="material-icons">check</i></span>
                                <span v-else>-</span>
                            </td>
                            <td class="right">
                                <span v-if="p.paid_amount" style="white-space: nowrap;">
                                    {{ displayDigits(p.paid_amount) }} kr.<br>
                                </span>
                                <span class="dim" style="white-space: nowrap;">
                                    {{ displayDigits(p.amount) }} kr.
                                </span>
                            </td>
                            </template>
                        </tr>
                    </tbody>
                </table>
            </template>
            <p v-if="payments.length < 1">
                Kunne ikke finde nogen sager
            </p>

            <!-- <button v-if="payments.length > 1" class="more">Vis flere</button> -->

        </div>

        <!-- <div class="payment-search-filters">
            <h2>Filtre</h2>
            <form>
                <fieldset>
                    <label>Betalingsnøgle</label>
                    <input @input="changeId()" type="text" v-model="field_id">
                </fieldset>
                <fieldset>
                    <legend>Tidsrum</legend>
                    <label>fra dato</label>
                    <input type="date">
                    <label>til dato</label>
                    <input type="date">
                </fieldset>
                <fieldset>
                    <input type="radio" id="field-paid-1" checked name="field-paid">
                    <label for="field-paid-1">Betalte og ubetalte</label>
                    <input type="radio" id="field-paid-2" name="field-paid">
                    <label for="field-paid-2">Kun betalte</label>
                    <input type="radio" id="field-paid-3" name="field-paid">
                    <label for="field-paid-3">Kun ubetalte</label>
                </fieldset>
                <fieldset>
                    <label>Hovedsag CPR</label>
                    <input type="text">
                </fieldset>
            </form>
        </div> -->

    </div>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import PaymentModal from './PaymentModal.vue'

    export default {
        
        components: {
            PaymentModal
        },
        data: function() {
            return {
                field_id: null
            }
        },
        computed: {
            payments: function() {
                return this.$store.getters.getPayments
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchPayments', this.$route.query)
            },
            changeId: function() {
                this.$route.query.id = this.field_id
                this.update()
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            }
        },
        created: function() {
            this.update()
        }

    }

</script>

<style>

    .payment-search {
        padding: 2rem;
        display: flex;
        flex-flow: row nowrap;
    }

    .payment-search-list {
        order: 2;
    }

    .payment-search-list .more .material-icons {
        margin: 0;
    }

    .payment-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 1rem;
        margin-right: 2rem;
    }

    .payment-search-filters h2,
    .payment-search-filters form {
        padding: 0;
    }

    .payment-search .more {
        width: 100%;
    }

</style>