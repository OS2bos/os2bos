<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section class="payment_schedule" v-if="payments_by_year">

        <div class="row" style="justify-items: space-between; flex-flow: row nowrap;">
            <header class="row payment-schedule-header">
                <h2 class="payment-schedule-title">
                    Betalinger <span style="opacity: .66;">betalingsnøgle {{ pId }}</span>
                </h2>
                <button class="btn payment-create-btn" title="Ny betaling" @click="payCreateDiagOpen" v-if="can_create_payment && !edit_mode">
                    + Tilføj betaling
                </button>
            </header>

            <fieldset class="payment-schedule-selector">
                <label for="field-year-picker">Vis betalinger fra år</label>
                <select id="field-year-picker" v-model="current_year">
                    <option v-for="y in years" :value="y" :key="y.id">{{ y }}</option>
                </select>
            </fieldset>
        </div>

        <payment-create-modal v-if="pay_create_diag_open" @closedialog="pay_create_diag_open = false" @paymentsaved="update" :plan="payment_plan" />
        
        <data-grid v-if="payments_by_year.length > 0"
            ref="data-grid"
            :data-list="payments_by_year"
            :columns="columns"
            class="payment_schedule_list"
            @update="updatePayment">

            <p slot="datagrid-header">
                Viser {{payments_by_year.length}} betalinger for {{ current_year }}
            </p>

        </data-grid>
        <p v-else>
            Der er ingen betalinger for det valgte år
        </p>
        
        <table v-if="payments_by_year.length > 0" class="payments-sum">
            <thead>
                <tr>
                    <th></th>
                    <th class="right">Planlagt</th>
                    <th class="right">Betalt</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th class="right dim">I alt i året {{ current_year }}</th>
                    <td class="right dim">{{ displayDigits(sum_expected) }} kr.</td>
                    <td class="right">{{ displayDigits(sum_paid) }} kr.</td>
                </tr>
            </tbody>
        </table>

    </section>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import PaymentCreateModal from './payment-editing/PaymentCreate.vue'
    import PermissionLogic from '../mixins/PermissionLogic.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import SaveButton from './datagrid-components/SaveButton.vue'
    import EditButton from './datagrid-components/EditButton.vue'
    import AmountInput from './datagrid-components/AmountInput.vue'
    import DateInput from './datagrid-components/DateInput.vue'
    import NoteInput from './datagrid-components/NoteInput.vue'

    export default {

        components: {
            PaymentCreateModal,
            DataGrid,
            SaveButton,
            EditButton,
            AmountInput,
            DateInput,
            NoteInput
        },
        mixins: [
            PermissionLogic
        ],
        props: [
            'pId',
            'edit_mode'
        ],
        data: function() {
            return {
                now: new Date(),
                years: [],
                current_year: null,
                pay_create_diag_open: false,
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
                        key: 'payment_schedule__payment_id',
                        title: 'Betalingsnøgle',
                        class: 'center'
                    },
                    {
                        key: 'account_string',
                        title: 'Kontostreng',
                        class: 'account-cell'
                    },
                    {
                        key: 'account_alias',
                        title: 'Kontoalias'
                    },
                    {
                        key: 'amount',
                        title: 'Planlagt beløb',
                        display_func: this.displayPlannedAmount,
                        class: 'right nowrap'
                    },
                    {
                        key: 'date',
                        title: 'Planlagt dato',
                        display_func: this.displayPlannedPayDate,
                        class: 'nowrap'
                    },
                    {
                        key: 'paid_amount',
                        title: 'Betalt beløb',
                        display_component: AmountInput,
                        class: 'right nowrap'
                    },
                    {
                        key: 'paid_date',
                        title: 'Betalt dato',
                        display_component: DateInput,
                        class: 'nowrap'
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
            payment_plan: function() {
                return this.$store.getters.getPaymentPlan
            },
            payments: function() {
                console.log('new payments in paymentlist.vue')
                return this.$store.getters.getPayments
            },
            payments_by_year: function() {
                let state_payments = this.$store.getters.getPayments
                if (state_payments) {
                    let payms = state_payments.filter(p => {
                        return this.current_year === parseInt(p.date.substr(0,4))
                    })
                    return payms
                } else {
                    return false
                }
            },
            sum_expected: function() {
                if (this.payments_by_year) {
                    return this.payments_by_year.reduce(function(total, payment) {
                        return total += parseFloat(payment.amount)
                    }, 0)
                }
            },
            sum_paid: function() {
                if (this.payments_by_year) {
                    return this.payments_by_year.reduce(function(total, payment) {
                        if (payment.paid_amount !== null) {
                            return total += parseFloat(payment.paid_amount)
                        } else {
                            return total
                        }
                    }, 0)
                }
            }
        },
        watch: {
            pId: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchPaymentPlan', this.pId)
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
                    this.$store.dispatch('updatePayment', updated_payment)
                } else {
                    this.$store.commit('setPayment', payload.data)
                }
            },
            displayPaidIcon: function(payment) {
                if (payment.paid) {
                    return '<i class="material-icons">check</i>'
                } else {
                    return '-'
                }
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
            },
            payCreateDiagOpen: function() {
                this.pay_create_diag_open = true
            },
            displayId: function(payment) {
                let str = `<button ref="edit-${ payment.id }">Betaling #${ payment.id }</button>`
                if (payment.payment_schedule__fictive) {
                    str += ` <span class="fictive">(Fiktiv)</span>`
                }
                return str
            },
            displayPlannedPayDate: function(payment) {
                return json2jsDate(payment.date)
            },
            displayPlannedAmount: function(payment) {
                return `${ cost2da(payment.amount) } kr`
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
        justify-content: flex-end;
        margin: 0;
        padding: 2rem 0 0;
        width: 20rem;
    }

    .payment-schedule-selector label {
        margin: 0 .5rem 0 0;
    }

    .payment-schedule-header {
        padding: 2rem 0 0;
        align-items: center;
    }

    .payment-schedule-title {
        padding: 0;
        margin-right: 1rem;
    }

    .payment-create-btn {
        margin: 0;
    }

    .payment-modal .payment-link {
        border-width: 0 0 1px 0;
        border-radius: 0;
        box-shadow: none;
        background-color: transparent;
        padding: 0;
        height: auto;
        font-size: 1rem;
    }

    .payment-modal .payment-link:hover,
    .payment-modal .payment-link:active {
        color: var(--grey10);
        border-color: var(--grey10);
    }

    .payment_schedule .datagrid-container {
        width: 100%;
        overflow: auto;
    }

    .payment_schedule .datagrid {
        table-layout: inherit;
    }

    .payment_schedule .datagrid td a:link,
    .payment_schedule .datagrid td a:visited,
    .payment_schedule .datagrid td a:hover, 
    .payment_schedule .datagrid td a:active {
        transition: none;
        padding-left: 1.5rem;
    }

    .payment_schedule .field-amount {
        width: 7rem;
    }

    .payment_schedule .field-note {
        width: 7rem;
    }

    .payment_schedule .account-cell {
        width: 15rem;
        white-space: nowrap;
    }

    .payment_schedule .payments-sum {
        width: auto;
        float: right;
        margin-top: 0;
        min-width: 40rem;
    }

    .payment_schedule_list td {
        overflow: visible;
    }

</style>
