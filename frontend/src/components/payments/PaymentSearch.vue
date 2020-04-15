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
            <template v-if="results">
            <span>{{results.length}} af {{payments.count}}</span>
                <table v-if="results.length > 0">
                    <thead>
                        <tr>
                            <th>Betaling nr</th>
                            <th>Betalingsnøgle</th>
                            <th>Betalingsmåde</th>
                            <th>Udbetales til</th>
                            <th>CPR nr</th>
                            <th>Betalingsdato</th>
                            <th>Betalt</th>
                            <th class="right">Beløb</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in results" :key="p.id">
                            <td>
                                <payment-modal :p-id="p.id" @update="update()"/>
                                <span class="dim" v-if="p.payment_schedule__fictive">(Fiktiv)</span>
                            </td>
                            <td> {{ p.payment_schedule__payment_id }} </td>
                            <td> 
                                <div v-if="p.payment_method === 'INVOICE'">Faktura</div>
                                <div v-if="p.payment_method === 'INTERNAL'">Intern afregning</div>
                                <div v-if="p.payment_method === 'CASH'">Udbetaling</div>
                                <div v-if="p.payment_method === 'SD'">SD-løn</div>
                            </td>
                            <td> 
                                {{ p.recipient_name }}<br>
                                <span v-if="p.recipient_type === 'COMPANY'">
                                    CVR
                                </span>
                                {{ p.recipient_id }}
                            </td>
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
                        </tr>
                    </tbody>
                </table>
                <p class="nopays" v-if="results.length < 1">
                    Kan ikke finde nogen betalinger
                </p>

                <button v-if="results.length > 1" :disabled="disableBtn" class="more" @click="loadResults()">Vis flere</button>
            </template>

        </div>

        <div class="payment-search-filters">
            <h2>Filtre</h2>
            <form>
                <fieldset>
                    <label for="field-pay-key">Betalingsnøgle</label>
                    <input id="field-pay-key" type="search" @input="update()" v-model="$route.query.payment_schedule__payment_id">
                </fieldset>
                <fieldset>
                    <legend>Tidsrum</legend>
                    <label for="field-from">Fra dato</label>
                    <input id="field-from" type="date" @input="update()" v-model="$route.query.paid_date_or_date__gte">
                    <label for="field-to">Til dato</label>
                    <input id="field-to" type="date" @input="update()" v-model="$route.query.paid_date_or_date__lte">
                </fieldset>
                <fieldset>
                    <input type="radio" id="field-paid-1" checked name="field-paid" :value="null" v-model="$route.query.paid" @change="update()">
                    <label for="field-paid-1">Betalte og ubetalte</label>
                    <input type="radio" id="field-paid-2" name="field-paid" :value="true" v-model="$route.query.paid" @change="update()">
                    <label for="field-paid-2">Kun betalte</label>
                    <input type="radio" id="field-paid-3" name="field-paid" :value="false" v-model="$route.query.paid" @change="update()">
                    <label for="field-paid-3">Kun ubetalte</label>
                </fieldset>
                <fieldset>
                    <label for="field-cpr">Hovedsag CPR</label>
                    <input id="field-cpr" type="search" @input="changeCpr" v-model="$route.query.case__cpr_number">
                </fieldset>
                <fieldset>
                    <label for="field-pay-method">Betalingsmåde</label>
                    <list-picker 
                        domId="field-pay-method"
                        :list="payment_methods"
                        @selection="changePaymentMethod" />
                </fieldset>
            </form>
        </div>

    </div>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import PaymentModal from './PaymentModal.vue'
    import CaseFilters from '../mixins/CaseFilters.js'
    import ListPicker from '../forms/ListPicker.vue'

    export default {
        
        components: {
            PaymentModal,
            ListPicker
        },
        mixins: [
            CaseFilters
        ],
        data: function() {
            return {
                input_timeout: null,
                payment_methods: [
                    {
                        id: 0,
                        name: 'Faktura',
                        sys_name: 'INVOICE'
                    },
                    {
                        id: 1,
                        name: 'Intern afregning',
                        sys_name: 'INTERNAL'
                    },
                    {
                        id: 2,
                        name: 'Udbetaling',
                        sys_name: 'CASH'
                    },
                    {
                        id: 3,
                        name: 'SD-løn',
                        sys_name: 'SD'
                    }
                ]
            }
        },
        computed: {
            payments: function() {
                return this.$store.getters.getPayments
            },
            results: function() {
                return this.payments.results
            },
            query: function() {
                return this.$route.query
            },
            disableBtn: function () {
                if (this.payments.next === null) {
                    return true
                }
            }
        },
        watch: {
            query: function() {
                this.update()
            }
        },
        methods: {
            loadResults: function() {
                this.$store.dispatch('fetchMorePayments')
            },
            changePaymentMethod: function(method) {
                if (method !== null) {
                    this.$route.query.payment_method = this.payment_methods[method].sys_name
                } else {
                    this.$route.query.payment_method = ''
                }
                this.update()
            },
            update: function() {
                clearTimeout(this.input_timeout)
                this.input_timeout = setTimeout(() => {
                    this.$store.dispatch('fetchPayments', this.$route.query)
                }, 300)
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
        padding: 1.5rem 1rem .5rem;
        margin: 0 2rem 1rem 0;
    }

    .payment-search-filters h2,
    .payment-search-filters form {
        padding: 0;
    }

    .payment-search .more {
        width: 100%;
    }

    .nopays {
        margin: 1rem 0;
    }

</style>