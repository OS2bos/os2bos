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
                <p>Viser {{results.length}} af {{payments.count}} betalinger</p>
                <table v-if="results.length > 0">
                    <thead>
                        <tr>
                            <th>ID</th>
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
                                <a @click="navToLink(`/activity/${ p.activity__id }`)">{{ p.id }} - {{ activityId2name(p.activity__details__id) }}</a>
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
                                <span class="dim" style="white-space: nowrap;">
                                    {{ displayDate(p.date) }}
                                </span>
                            </td>
                            <td>
                                <span class="dim" style="white-space: nowrap;">
                                    {{ displayDigits(p.amount) }} kr.
                                </span>
                            </td>

                         <template v-if="paymentlock && !p.is_payable_manually">
                            <td>
                                {{ displayDate(p.paid_date) }}
                            </td>
                            <td>
                                {{ displayDigits(p.paid_amount) }} kr.
                            </td>
                            <td>
                                <span v-if="p.note">{{ p.note }}</span>
                                <span v-else>-</span>
                            </td>
                            <td></td>
                         </template>

                         <template v-if="permissionCheck === true && p.activity__status === 'GRANTED' && p.is_payable_manually">
                            <td>
                                <input type="date" :id="`field-date-${ p.id }`" v-model="p.date" required>
                            </td>
                            <td>
                                <input type="number" :id="`field-amount-${ p.id }`" step="0.01" v-model="p.amount" required>
                            </td>
                            <td>
                                <input type="text" :id="`field-note-${ p.id }`" v-model="p.note">
                            </td>
                            <td>
                                <button 
                                    v-if="p.activity__status === 'GRANTED'" 
                                    type="button" 
                                    :disabled="p.amount && p.date ? false : true" 
                                    @click="pay()">
                                    Betal
                                </button>
                            </td>
                         </template>
                        </tr>
                    </tbody>
                </table>
                <p class="nopays" v-if="results.length < 1">
                    Kan ikke finde nogen betalinger
                </p>

                <button v-if="results.length > 1" :disabled="disableBtn" class="more" @click="loadResults()">Vis flere</button>
            </template>
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
    import { activityId2name } from '../filters/Labels.js'

    export default {
        
        components: {
            PaymentModal,
            ListPicker
        },
        mixins: [
            CaseFilters, UserRights
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
            pay: function() {
                let data = {
                    paid_amount: this.p.amount,
                    paid_date: this.p.date,
                    note: this.p.note ? this.p.note : '',
                    paid: true
                }
                axios.patch(`/payments/${ this.payment.id }/`, data)
                .then(res => {
                    notify('Betaling godkendt', 'success')
                    this.update()
                    this.$emit('update')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            activityId2name: function(id) {
                return activityId2name(id)
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

    .payment-search-list .more .material-icons {
        margin: 0;
    }

    .payment-search .more {
        width: 100%;
    }

    .nopays {
        margin: 1rem 0;
    }

</style>