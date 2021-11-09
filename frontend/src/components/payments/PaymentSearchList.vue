<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="payment-search-list">
        <template v-if="payments && payments.length > 0">
            
            <data-grid
                ref="data-grid"
                :data-list="payments"
                :columns="columns"
                @selection="selected_payments"
                @update="updatePayment">

                <p slot="datagrid-header">
                    Viser {{ payments.length }} af {{ payments_meta.count }} betalinger
                </p>

            </data-grid>

            <button v-if="payments_meta.next" class="more" @click="loadResults">Vis flere</button>
        </template>

        <p v-else>
            Der er ingen betalinger, som matcher de valgte kriterier
        </p>

    </div>

</template>

<script>
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, displayPayMethod } from '../filters/Labels.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import SaveButton from './datagrid-components/SaveButton.vue'
    import AmountInput from './datagrid-components/AmountInput.vue'
    import DateInput from './datagrid-components/DateInput.vue'
    import NoteInput from './datagrid-components/NoteInput.vue'
    import EditButton from './datagrid-components/EditButton.vue'

    export default {
        
        components: {
            DataGrid,
            SaveButton,
            AmountInput,
            DateInput,
            NoteInput,
            EditButton
        },
        data: function() {
            return {
                selected_payments: [],
                columns: [
                    {
                        key: 'id',
                        title: 'Betaling',
                        display_component: EditButton,
                        class: 'datagrid-action nowrap'
                    },
                    {
                        key: 'paid',
                        title: 'Betalt',
                        display_func: this.displayPaidIcon,
                        class: 'center'
                    },
                    {
                        key: 'activity_id',
                        title: 'Aktivitet',
                        display_func: this.displayId,
                        class: 'datagrid-action nowrap'
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
                        key: 'activity__note',
                        title: 'Supplerende oplysninger (aktivitet)',
                        display_func: this.displayActivityNote
                    },
                    {
                        key: 'case__cpr_number',
                        title: 'Hovedsag CPR-nr',
                        display_func: this.displayCprName
                    },
                    {
                        key: 'account_string',
                        title: 'Kontostreng',
                        display_func: this.displayAccounts,
                        class: 'nowrap'
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
                        display_component: AmountInput,
                        class: 'nowrap'
                    },
                    {
                        key: 'paid_date',
                        title: 'Betalt dato',
                        display_component: DateInput,
                        class: 'nowrap overflow'
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
            payments_meta: function() {
                return this.$store.getters.getSearchPaymentsMeta
            },
            payments: function() {
                return this.$store.getters.getSearchPayments
            }
        },
        methods: {
            displayId: function(payment) {
                let str = `<a href="/#/activity/${ payment.activity__id }">${ activityId2name(payment.activity__details__id) }</a>`
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
            displayActivityNote: function(payment) {
                const note = payment.activity__note
                if (note.length > 150) {
                  return `${note.substr(0, 150)} [...]`
                }
                return note
            },
            displayCprName: function(id) {
                return `${ id.case__name }<br>${ id.case__cpr_number }`
            },
            loadResults: function() {
                this.$store.dispatch('fetchMoreSearchPayments')
            },
            displayPlannedPayDate: function(payment) {
                return json2jsDate(payment.date)
            },
            displayPlannedAmount: function(payment) {
                return `${ cost2da(payment.amount) } kr`
            },
            displayAccounts: function(payment) {
                let str = `${ payment.account_string }`
                if (payment.account_alias){
                    str += `<dl><dt>Kontoalias</dt><dd>${ payment.account_alias }</dd></dl>`
                } else {
                    str
                }
                return str
            },
            displayPaidIcon: function(payment) {
                if (payment.paid) {
                    return '<i class="material-icons">check</i>'
                } else {
                    return '-'
                }
            },
            updatePayment: function(payload) {
                if (payload.operation === 'save') {
                    const updated_payment = {
                        id: payload.data.id,
                        paid_amount: payload.data.paid_amount,
                        paid_date: payload.data.paid_date,
                        note: payload.data.note ? payload.data.note : '',
                        paid: true
                    }
                    this.$store.dispatch('updateSearchPayment', updated_payment)
                } else if (payload.operation === 'replan') {
                    const updated_payment = {
                        id: payload.data.id,
                        amount: payload.data.amount,
                        date: payload.data.date
                    }
                    this.$store.dispatch('updateSearchPayment', updated_payment)
                } else {
                    this.$store.commit('setSearchPayment', payload.data)
                }
            }
        }
    }

</script>

<style>

    .payment-search-list {
        margin-top: 2rem;
        flex-grow: 1;
    }

    .payment-search-list .datagrid-container {
        width: 100%;
        overflow: auto;
    }

    .payment-search-list .datagrid {
        table-layout: inherit;
    }

    .payment-search-list .datagrid .datagrid-action {
        padding-left: .75rem;
    }

    .payment-search-list .field-amount {
        width: 7rem;
    }

    .payment-search-list .field-note {
        width: 7rem;
    }

    .payment-search-list .more .material-icons {
        margin: 0;
    }

    .payment-search-list .more {
        width: 100%;
    }

    .payment-search-list .fictive {
        padding: 0rem 1.5rem;
    }

    .payment-search-list .overflow {
        overflow: visible;
    }

</style>