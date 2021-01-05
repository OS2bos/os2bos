<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="search-filter payment-search-filters">
        <form @submit.prevent>
            <fieldset class="filter-fields">
                <div class="filter-field">
                    <label for="field-pay-key">Betalingsnøgle</label>
                    <input id="field-pay-key" type="search" v-model="payment_schedule__payment_id">
                </div>

                <div class="filter-field">
                    <label for="field-cpr">Hovedsag CPR nr.</label>
                    <input id="field-cpr" type="search" v-model="case__cpr_number">
                </div>

                <div class="filter-field">
                    <label for="field-payee">Betalingsmodtager</label>
                    <input id="field-payee" type="search" v-model="recipient_id">
                </div>

                <div class="filter-field">
                    <label for="field-pay-method">Betalingsmåde</label>
                    <list-picker
                        v-if="payment_methods"
                        domId="field-pay-method"
                        :selected-id="payment_method"
                        :list="payment_methods"
                        @selection="changePaymentMethod" />
                </div>

                <div class="filter-field">
                    <label for="field-pay-method">Tidsinterval</label>
                    <list-picker
                        v-if="intervals"
                        domId="field-time-interval"
                        :selected-id="interval"
                        :list="intervals"
                        @selection="changeTimeInterval" />
                </div>

                <template v-if="range_dates === true">
                    <div class="filter-field">
                        <label for="field-from">Fra dato</label>
                        <input id="field-from" type="date" @input="update" v-model="paid_date_or_date__gte">
                    </div>

                    <div class="filter-field">
                        <label for="field-to">Til dato</label>
                        <input id="field-to" type="date" @input="update" v-model="paid_date_or_date__lte">
                    </div>
                </template>
            </fieldset>

            <fieldset class="filter-fields radio-filters">
                <div class="filter-field">
                    <input type="radio" id="field-paid-1" checked name="field-paid" :value="null" v-model="paid">
                    <label for="field-paid-1">Betalte og ubetalte</label>
                </div>
                <div class="filter-field">
                    <input type="radio" id="field-paid-2" name="field-paid" :value="true" v-model="paid">
                    <label for="field-paid-2">Kun betalte</label>
                </div>
                <div class="filter-field">
                    <input type="radio" id="field-paid-3" name="field-paid" :value="false" v-model="paid">
                    <label for="field-paid-3">Kun ubetalte</label>
                </div>
            </fieldset>

            <fieldset class="filter-fields filter-actions">
                <button class="filter-reset" type="reset" @click="resetValues">Nulstil</button>
            </fieldset>
        </form>
    </div>
</template>

<script>

    import ListPicker from '../forms/ListPicker.vue'
    import TimeIntervalFilters from '../mixins/TimeIntervalFilters.js'
    import Timeout from '../mixins/Timeout.js'

    export default {
        components: {
            ListPicker
        },
        mixins: [
            TimeIntervalFilters,
            Timeout
        ],
        data: function() {
            return {
                range_dates: false,
                payment_methods: [
                    {
                        id: 1,
                        name: 'Faktura',
                        sys_name: 'INVOICE'
                    },
                    {
                        id: 2,
                        name: 'Intern afregning',
                        sys_name: 'INTERNAL'
                    },
                    {
                        id: 3,
                        name: 'Udbetaling',
                        sys_name: 'CASH'
                    },
                    {
                        id: 4,
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
            // Search filters:
            payment_schedule__payment_id: {
                get: function() {
                    // Get search filter saved in store. Displays in input field via `v-model`
                    return this.$store.getters.getPaymentSearchFilter('payment_schedule__payment_id')
                },
                set: function(new_val) {
                    // When user changes value in input field, commit the new value
                    // The `commitValue` helper method has a debounce feature, in order to avoid request spamming.
                    // This method is handy for values that the user types into text fields.
                    this.commitValue('payment_schedule__payment_id', new_val)
                }
            },
            case__cpr_number: {
                get: function() {
                    return this.$store.getters.getPaymentSearchFilter('case__cpr_number')
                }, 
                set: function(new_val) {
                    this.commitValue('case__cpr_number', new_val)
                }
            },
            recipient_id: {
                get: function() {
                    return this.$store.getters.getPaymentSearchFilter('recipient_id')
                }, 
                set: function(new_val) {
                    this.commitValue('recipient_id', new_val)
                }
            },
            payment_method: function() {
                // `payment_method` only has a getter. values are updated via changePaymentMethod method in listpicker component
                const filter = this.$store.getters.getPaymentSearchFilter('payment_method')
                if (filter) {
                    const method = this.payment_methods.find(method => method.sys_name === filter)
                    if (method) {
                        return method.id
                    }
                }
                return null
            },
            interval: function() {
                // `interval` only has a getter. values are updated via changeTimeInterval method in listpicker component
                return this.$store.getters.getPaymentSearchFilter('interval')
            },
            paid_date_or_date_week: function() {
                // `paid_date_or_date_week` only has a getter. values are updated via changeTimeInterval method in listpicker component
                return this.$store.getters.getPaymentSearchFilter('paid_date_or_date_week')
            },
            paid_date_or_date_month: function() {
                // `paid_date_or_date_month` only has a getter. values are updated via changeTimeInterval method in listpicker component
                return this.$store.getters.getPaymentSearchFilter('paid_date_or_date_month')
            },
            paid_date_or_date_year: function() {
                // `paid_date_or_date_year` only has a getter. values are updated via changeTimeInterval method in listpicker component
                return this.$store.getters.getPaymentSearchFilter('paid_date_or_date_year')
            },
            paid_date_or_date__gte: {
                get: function() {
                    return this.$store.getters.getPaymentSearchFilter('paid_date_or_date__gte')
                }, 
                set: function(new_val) {
                    this.$store.commit('setPaymentSearchFilter', {'paid_date_or_date__gte': new_val})
                }
            },
            paid_date_or_date__lte: {
                get: function() {
                    return this.$store.getters.getPaymentSearchFilter('paid_date_or_date__lte')
                }, 
                set: function(new_val) {
                    this.$store.commit('setPaymentSearchFilter', {'paid_date_or_date__lte': new_val})
                }
            },
            paid: {
                get: function() {
                    return this.$store.getters.getPaymentSearchFilter('paid')
                }, 
                set: function(new_val) {
                    // When user changes value in radio button, commit the new value
                    // We don't use the `commitValue` helper method here.
                    this.$store.commit('setPaymentSearchFilter', {'paid': new_val})
                    this.$store.dispatch('fetchPayments')
                }
            },
            update: function() {
                this.$store.dispatch('fetchPayments')
            }
        },
        methods: {
            resetValues: function() {
                // Reset store values for payment search filters
                this.$store.dispatch('resetPaymentSearchFilters')
            },
            commitValue: function(key, val) {
                // Handy helper method that both updates the value in store, 
                // dispatches a request to get an updated list of cases,
                // and is debounced to avoid API request spam.
                this.$store.commit('setPaymentSearchFilter', {[key]: val})
                this.$store.dispatch('fetchPayments')
            },
            changePaymentMethod: function(methodId) {
                // Checks if anything has actually been changed and updates store values
                // + fetches an updated list of payments
                if (this.payment_method !== methodId && this.payment_method || methodId) {
                    if (methodId) {
                        const method = this.payment_methods.find(method => method.id === methodId).sys_name
                        this.$store.commit('setPaymentSearchFilter', {'payment_method': method})
                    } else {
                        this.$store.commit('setPaymentSearchFilter', {'payment_method': ''})
                    }
                    this.$store.dispatch('fetchPayments')
                }
            }
        },
        created: function() {

            // Set debounce on methods that are likely to be fired too often
            // (ie. while a user is typing into an input field)
            this.commitValue = this.debounce(this.commitValue, 400)

            // On first load, check URL params and set store filters accordingly
            const qry = this.$route.query
            if (qry.payment_schedule__payment_id || qry.recipient_id || qry.payment_method || qry.interval || qry.paid_date_or_date_week || qry.paid_date_or_date_month || qry.paid_date_or_date_year || qry.paid_date_or_date__gte || qry.paid_date_or_date__lte || qry.hasOwnProperty('paid') && qry.paid !== null) {
                this.$store.commit('setPaymentSearchFilter', qry)
                this.$store.dispatch('fetchPayments')
            }

            // Show 'range_dates' if interval is 'date-range'
            if (this.interval === 'date-range') {
                this.range_dates = true
            }

        }
    }

</script>

<style>

    .payment-search-filters .radio-filters {
        margin-top: 1rem;
    }

    .payment-search-filters .filter-actions {
        flex-grow: 1;
        text-align: right;
    }

    .payment-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 0 1.5rem 1rem;
    }

</style>