<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div class="payment-search">

        <div class="payment-search-filters">
            <h2 class="payment-search-filters--title">Filtrér betalinger</h2>
            <form>
                <ul class="filter-fields">
                    <li>
                        <label for="field-pay-key">Betalingsnøgle</label>
                        <input id="field-pay-key" type="search" @input="update()" v-model="$route.query.payment_schedule__payment_id">
                    </li>

                    <li>
                        <label for="field-cpr">Hovedsag CPR nr.</label>
                        <input id="field-cpr" type="search" @input="changeCpr" v-model="$route.query.case__cpr_number">
                    </li>

                    <li>
                        <label for="field-payee">Betalingsmodtager</label>
                        <input id="field-payee" type="search" @input="update()" v-model="$route.query.recipient_id">
                    </li>

                    <li>
                        <label for="field-pay-method">Betalingsmåde</label>
                        <list-picker 
                            domId="field-pay-method"
                            :list="payment_methods"
                            @selection="changePaymentMethod" />
                    </li>

                    <li>
                        <label for="field-from">Fra dato</label>
                        <input id="field-from" type="date" @input="update()" v-model="$route.query.paid_date_or_date__gte">
                    </li>
                    <li>
                        <label for="field-to">Til dato</label>
                        <input id="field-to" type="date" @input="update()" v-model="$route.query.paid_date_or_date__lte">
                    </li>
                </ul>

                <ul class="filter-fields">
                    <li>
                        <input type="radio" id="field-paid-1" checked name="field-paid" :value="null" v-model="$route.query.paid" @change="update()">
                        <label for="field-paid-1">Betalte og ubetalte</label>
                    </li>
                    <li>
                        <input type="radio" id="field-paid-2" name="field-paid" :value="true" v-model="$route.query.paid" @change="update()">
                        <label for="field-paid-2">Kun betalte</label>
                    </li>
                    <li>
                        <input type="radio" id="field-paid-3" name="field-paid" :value="false" v-model="$route.query.paid" @change="update()">
                        <label for="field-paid-3">Kun ubetalte</label>
                    </li>
                </ul>
            </form>
        </div>

        <div class="payment-search-list">
            <h1>Betalinger</h1>
            <template v-if="results">
            <span>{{results.length}} af {{payments.count}}</span>
                <table v-if="results.length > 0">
                    <thead>
                        <tr>
                            <th>Betaling nr</th>
                            <th>Betalingsnøgle</th>
                            <th>Betalingsmåde/modtager</th>
                            <th>Hovedsag CPR nr./ kontostreng</th>
                            <th>Planlagt betalingsdato</th>
                            <th>Planlagt beløb</th>
                            <th>Betalt dato</th>
                            <th>Betalt beløb</th>
                            <th>Reference</th>
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
                                {{ p.recipient_name }}<br>
                                <span v-if="p.recipient_type === 'COMPANY'">
                                    CVR
                                </span>
                                {{ p.recipient_id }}
                            </td>
                            <td>
                                {{ p.case__cpr_number }} <br>
                                {{ p.account_string }}
                            </td>
                            <td>
                                <span v-if="p.paid_date" style="white-space: nowrap;">
                                    {{ displayDate(p.paid_date) }}<br>
                                </span>
                                <span class="dim" style="white-space: nowrap;">
                                    {{ displayDate(p.date) }}
                                </span>
                            </td>
                            <td>
                                <span v-if="p.paid_amount" style="white-space: nowrap;">
                                    {{ displayDigits(p.paid_amount) }} kr.<br>
                                </span>
                                <span class="dim" style="white-space: nowrap;">
                                    {{ displayDigits(p.amount) }} kr.
                                </span>
                            </td>
                            <td>
                                <input type="date" :id="`field-date-${ p.id }`" v-model="p.paid_date" required>
                            </td>
                            <td>
                                <input type="number" :id="`field-amount-${ p.id }`" step="0.01" v-model="p.paid_amount" required>
                            </td>
                            <td>
                                <input type="text" :id="`field-note-${ p.id }`" v-model="p.note">
                            </td>
                            <td>
                                <button class="modal-confirm-btn" type="submit">Gem</button>
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
        padding: 0 2rem 2rem;
    }

    .payment-search-list {
        margin-top: 2rem;
        order: 2;
        flex-grow: 1;
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

    .payment-search-filters--title {
        font-size: 1.125rem;
        padding: 1.5rem 0 .5rem;
    }

    .payment-search-filters > form {
        padding: 0;
    }

    .payment-search-filters .filter-fields {
        margin: 0;
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        align-items: flex-start;
    }

    .payment-search-filters .filter-fields li {
        list-style: none;
        padding: .5rem 1rem .5rem 0;
    }

    .payment-search-filters .filter-fields label {
        margin: 0;
    }

    .payment-search .more {
        width: 100%;
    }

    .nopays {
        margin: 1rem 0;
    }

    .input-pay {
        width: 5rem;
    }

</style>