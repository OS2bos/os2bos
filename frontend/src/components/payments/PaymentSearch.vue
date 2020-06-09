<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <section class="payment-search">
        
        <header>
            <h1>Betalinger</h1>
        </header>

        <div class="search-filter">
            <form>
                <fieldset class="filter-fields">
                    <div class="filter-field">
                        <label for="field-pay-key">Betalingsnøgle</label>
                        <input id="field-pay-key" type="search" @input="update()" v-model="$route.query.payment_schedule__payment_id">
                    </div>

                    <div class="filter-field">
                        <label for="field-cpr">Hovedsag CPR nr.</label>
                        <input id="field-cpr" type="search" @input="changeCpr" v-model="$route.query.case__cpr_number">
                    </div>

                    <div class="filter-field">
                        <label for="field-payee">Betalingsmodtager</label>
                        <input id="field-payee" type="search" @input="update()" v-model="$route.query.recipient_id">
                    </div>

                    <div class="filter-field">
                        <label for="field-pay-method">Betalingsmåde</label>
                        <list-picker 
                            domId="field-pay-method"
                            :list="payment_methods"
                            @selection="changePaymentMethod" />
                    </div>

                    <div class="filter-field">
                        <label for="field-from">Fra dato</label>
                        <input id="field-from" type="date" @input="update()" v-model="$route.query.paid_date_or_date__gte">
                    </div>

                    <div class="filter-field">
                        <label for="field-to">Til dato</label>
                        <input id="field-to" type="date" @input="update()" v-model="$route.query.paid_date_or_date__lte">
                    </div>
                </fieldset>

                <fieldset class="filter-fields radio-filters">
                    <div class="filter-field">
                        <input type="radio" id="field-paid-1" checked name="field-paid" :value="null" v-model="$route.query.paid" @change="update()">
                        <label for="field-paid-1">Betalte og ubetalte</label>
                    </div>
                    <div class="filter-field">
                        <input type="radio" id="field-paid-2" name="field-paid" :value="true" v-model="$route.query.paid" @change="update()">
                        <label for="field-paid-2">Kun betalte</label>
                    </div>
                    <div class="filter-field">
                        <input type="radio" id="field-paid-3" name="field-paid" :value="false" v-model="$route.query.paid" @change="update()">
                        <label for="field-paid-3">Kun ubetalte</label>
                    </div>
                </fieldset>
            </form>
        </div>

        <div class="payment-search-list">
            <template v-if="results">
                
                <data-grid v-if="results.length > 0"
                    ref="data-grid"
                    :data-list="results"
                    :columns="columns">

                    <p slot="datagrid-header">
                        Viser {{results.length}} af {{payments.count}} betalinger
                    </p>

                    <p slot="datagrid-footer" v-if="results.length < 1">
                        Kan ikke finde nogen betalinger, der matcher de valgte kriterier
                    </p>

                </data-grid>

                <button v-if="results.length > 1" :disabled="disableBtn" class="more" @click="loadResults()">Vis flere</button>
            </template>
            <p v-else>
                Der er ingen betalinger, der matcher de valgte kriterier
            </p>
        </div>

    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import Error from '../forms/Error.vue'
    import notify from '../notifications/Notify.js'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import PaymentModal from './PaymentModal.vue'
    import CaseFilters from '../mixins/CaseFilters.js'
    import ListPicker from '../forms/ListPicker.vue'
    import UserRights from '../mixins/UserRights.js'
    import { activityId2name, displayPayMethod } from '../filters/Labels.js'
    import DataGrid from '../datagrid/DataGrid.vue'

    import SaveButton from './datagrid-components/SaveButton.vue'
    import AmountInput from './datagrid-components/AmountInput.vue'
    import DateInput from './datagrid-components/DateInput.vue'
    import NoteInput from './datagrid-components/NoteInput.vue'

    export default {
        
        components: {
            DataGrid,
            PaymentModal,
            ListPicker,
            SaveButton,
            AmountInput,
            DateInput,
            NoteInput
        },
        mixins: [
            CaseFilters, 
            UserRights
        ],
        data: function() {
            return {
                input_timeout: null,
                paymentlock: true,
                p: {
                    amount: null,
                    date: null,
                    note: null
                },
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
                ],
                columns: [
                    {
                        key: 'id',
                        title: 'Betaling',
                        display_func: this.displayId,
                        class: 'datagrid-action'
                    },
                    {
                        key: 'payment_schedule__payment_id',
                        title: 'Betalingsnøgle',
                        class: 'center'
                    },
                    {
                        key: 'recipient_name',
                        title: 'Betalingsmodtager',
                        display_func: this.displayReceiver
                    },
                    {
                        key: 'case__cpr_number',
                        title: 'Hovedsag CPR-nr / Kontostreng',
                        display_func: this.displayCprAccount
                    },
                    {
                        key: 'amount',
                        title: 'Planlagt beløb',
                        display_func: this.displayPlannedAmount,
                        class: 'right'
                    },
                    {
                        key: 'date',
                        title: 'Planlagt betalingsdato',
                        display_func: this.displayPlannedPayDate
                    },
                    {
                        key: 'paid_amount',
                        title: 'Betalt beløb',
                        display_component: AmountInput
                    },
                    {
                        key: 'paid_date',
                        title: 'Betalt dato',
                        display_component: DateInput
                    },
                    {
                        key: 'note',
                        title: 'Reference',
                        display_component: NoteInput
                    },
                    {
                        display_component: SaveButton,
                        class: 'center'
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
            },
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        watch: {
            query: function() {
                this.update()
            }
        },
        methods: {
            displayId: function(payment) {
                let str = `<a href="/#/activity/${ payment.activity__id }">#${ payment.id } - ${ activityId2name(payment.activity__details__id) }</a>`
                if (payment.payment_schedule__fictive) {
                    str += `<span class="fictive">(Fiktiv)</span>`
                }
                return str
            },
            displayReceiver: function(payment) {
                let str = `<span class="label-header">${ displayPayMethod(payment.payment_method) }</span><br> ${ payment.recipient_name}`
                if (payment.recipient_type === 'COMPANY') {
                    str += `<br><span class="label-header">cvr</span> ${ payment.recipient_id}`
                } else if (payment.recipient_type === 'PERSON') {
                    str += `<br><span class="label-header">cpr</span> ${ payment.recipient_id}`
                } else {
                    str += `<br>${ payment.recipient_id}`
                }
                return str
            },
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
            displayPlannedPayDate: function(payment) {
                return json2jsDate(payment.date)
            },
            displayPlannedAmount: function(payment) {
                return `${ cost2da(payment.amount) } kr`
            },
            displayCprAccount: function(payment) {
                return `<span class="label-header">cpr</span> ${ payment.case__cpr_number } <br>${ payment.account_string }`
            },
            navToLink: function(path) {
                this.$router.push(path)
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

    .payment-search .radio-filters {
        margin-top: 1rem;
    }

    .payment-search-list {
        margin-top: 2rem;
        flex-grow: 1;
    }

    .payment-search .datagrid-container {
        width: 100%;
        overflow: auto;
    }

    .payment-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 0 1.5rem 1rem;
    }

    .payment-search .datagrid {
        table-layout: inherit;
    }

    .payment-search .datagrid td a:link,
    .payment-search .datagrid td a:visited,
    .payment-search .datagrid td a:hover, 
    .payment-search .datagrid td a:active {
        transition: none;
        padding-left: 1.5rem;
        
    }

    .payment-search .field-amount {
        width: 7rem;
    }

    .payment-search .field-note {
        width: 7rem;
    }

    .payment-search-list .more .material-icons {
        margin: 0;
    }

    .payment-search .more {
        width: 100%;
    }

    .payment-search .fictive {
        padding: 0rem 1.5rem;
    }

</style>