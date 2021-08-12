<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <modal-dialog @closedialog="closeDiag" class="payment-edit">

        <h2 slot="header" class="row payment-edit-header">
            <span class="payment-title">
                <span v-if="p.paid" class="label label-GRANTED" title="Betalt">
                    <i class="material-icons" style="width: 1.5rem;">checkmark</i>
                </span>
                Betaling #{{ p.id }}
                <span v-if="p.payment_schedule__fictive" class="dim">(Fiktiv)</span>
                <span v-if="p.paid_amount" class="dim">(Betalt)</span>
            </span>
            <button v-if="can_delete_payment" class="payment-delete-btn modal-delete-btn" @click="delete_diag_open = true">Slet</button>
        </h2>

        <div slot="body">

            <div class="payment-edit-body">
                <div>

                    <!-- Planned payment form -->
                    <form @submit.prevent="updatePlannedPayment" v-if="can_edit_payment" style="margin-bottom: .25rem;">
                        <error />
                        <fieldset>
                            <legend>Planlagt betaling</legend>

                            <label for="field-planned-amount" class="required">Beløb</label>
                            <input type="number" step="0.01" v-model="p.amount" id="field-planned-amount" required> kr

                            <label for="field-planned-date" class="required">Betalingsdato</label>
                            <input type="date" v-model="p.date" id="field-planned-date" required>

                            
                        </fieldset>
                        <fieldset style="margin-bottom: .75rem;">
                            <input type="submit" value="Opdatér">
                        </fieldset>
                    </form>

                    <!-- Planned payment info -->
                    <dl v-else style="margin-bottom: 1rem;">
                        <dt>Beløb, planlagt</dt>
                        <dd class="dim">{{ displayDigits(p.amount) }} kr.</dd>
                        <dt>Betalingsdato, planlagt</dt>
                        <dd class="dim">{{ displayDate(p.date) }}</dd>
                    </dl>

                    <!-- Pay payment form -->
                    <form @submit.prevent="pay" v-if="is_payable(payment)">
                        <error />
                        <fieldset>
                            <legend>Betaling</legend>
                            <label for="field-pay-amount" class="required">Betal beløb</label>
                            <input type="number" step="0.01" v-model="p.paid_amount" id="field-pay-amount" required>

                            <label for="field-pay-date" class="required">Betal dato</label>
                            <popover :condition="display_warning">{{ display_warning }}</popover>
                            <input :ref="`dateInput${ payment.id }`" type="date" v-model="p.paid_date" id="field-pay-date" required>

                            <label for="field-pay-note">Referencetekst</label>
                            <input type="text" v-model="p.note" id="field-pay-note">

                            <error err-key="note" />

                        </fieldset>
                        <fieldset style="margin-bottom: .75rem;">
                            <input type="submit" :disabled="disabled" value="Betal">
                        </fieldset>
                    </form>

                    <!-- Pay payment info -->
                    <dl v-else>
                        <dt>Betalt beløb</dt>
                        <dd>
                            {{ displayDigits(p.paid_amount) }} kr.
                        </dd>
                        <dt>Betalt dato</dt>
                        <dd>
                            {{ displayDate(p.paid_date) }}
                        </dd>
                        <template v-if="p.note">
                            <dt>Referencetekst</dt>
                            <dd>
                                {{ p.note }}
                            </dd>
                        </template>
                    </dl>

                </div>
                
                <div class="info">
                    <dl>
                        <dt>Ydelse</dt>
                        <dd v-if="p.activity__id">{{ activityId2name(p.activity__details__id) }}</dd>
                        <dt>Betalingsnøgle</dt>
                        <dd>{{ p.payment_schedule__payment_id }}</dd>
                    
                        <dt>Kontostreng</dt>
                        <dd>{{ p.account_string ? p.account_string : 'ukendt' }}</dd>
                    
                        <dt>Kontoalias</dt>
                        <dd>{{ p.account_alias ? p.account_alias : 'ukendt' }}</dd>
                    
                        <template v-if="p.payment_schedule__fictive">
                            <dt>Betaling</dt>
                            <dd>Fiktiv</dd>
                        </template>
                    </dl>

                    <hr style="margin: 1rem 0;">

                    <payment-details :payment="p" />

                </div>

            </div>

            <!-- Delete payment modal -->
            <modal-dialog v-if="delete_diag_open" @closedialog="delete_diag_open = false">
                <h3 slot="header">
                    Slet betaling
                </h3>
                <div slot="body">
                    <p>Er du sikker på, at du vil slette <strong>betaling #{{ p.id }}</strong> med beløb {{ displayDigits(p.amount) }} kr?</p>
                </div>
                <div slot="footer">
                    <form @submit.prevent="deletePayment" class="modal-form">
                        <input id="payment-confirm-delete" class="modal-delete-btn" type="submit" value="Slet">
                        <button class="modal-cancel-btn" type="button" @click="delete_diag_open = false">Annullér</button>
                    </form>
                </div>
            </modal-dialog>
            
        </div>

        <div slot="footer">
            <button type="button" class="modal-cancel-btn" @click="closeDiag">Luk</button>
        </div>

    </modal-dialog>

</template>

<script>
    import axios from '../../http/Http.js'
    import Error from '../../forms/Error.vue'
    import PermissionLogic from '../../mixins/PermissionLogic.js'
    import notify from '../../notifications/Notify.js'
    import { json2jsDate } from '../../filters/Date.js'
    import { cost2da } from '../../filters/Numbers.js'
    import { activityId2name } from '../../filters/Labels.js'
    import ModalDialog from '../../dialog/Dialog.vue'
    import Popover from '../../warnings/Popover.vue'
    import PaymentDetails from '../PaymentDetails.vue'

    export default {
        mixins: [
            PermissionLogic
        ],
        components: {
            Error,
            ModalDialog,
            Popover,
            PaymentDetails
        },
        props: [
            'payment'
        ],
        data: function() {
            return {
                delete_diag_open: false,
                display_warning: null
            }
        },
        computed: {
            p: function() {
                return this.payment
            },
            disabled: function() {
                if (this.payment.paid_amount && this.payment.paid_date || this.payment.amount && this.payment.date) {
                    return false
                } else {
                    return true
                }
            }
        },
        methods: {
            activityId2name: function(id) {
                return activityId2name(id)
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            pay: function() {
                if (!this.p.paid || this.user.profile === 'workflow_engine' || this.user.profile === 'admin') {
                    this.$emit('update', {operation: 'save', data: this.p})
                }
            },
            updatePlannedPayment: function() {
                this.$emit('update', {operation: 'replan', data: this.p})
            },
            closeDiag: function() {
                this.$store.dispatch('fetchPaymentPlan', this.p.payment_schedule)
                this.$store.commit('clearErrors')
                this.$emit('closedialog')
            },
            navToLink: function(path) {
                this.$emit('close')
                this.$router.push(path)
            },
            deletePayment: function() {
                axios.delete(`/payments/${ this.p.id }/`)
                .then(() => {
                    this.closeDiag()
                    notify('Betaling slettet', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            },
            focusHandler: function() {
                this.display_warning = this.warn_edit_payment(this.payment)
            },
            blurHandler: function() {
                this.display_warning = null
            }
        },
        mounted: function() {
            let input_id = `dateInput${ this.payment.id }`
            if (this.$refs[input_id]) {
                this.$refs[input_id].addEventListener('focus', this.focusHandler)
                this.$refs[input_id].addEventListener('blur', this.blurHandler)
            }
        }
    }

</script>

<style>

    .payment-edit .modal-container {
        width: auto;
        max-width: 90vw;
    }

    .payment-edit-header {
        align-items: center;
        padding: 0;
    }

    .payment-edit .modal-delete-btn {
        margin: 0 0 0 .75rem !important;
        float: none;
    }

    .payment-edit-body {
        margin-top: 1rem;
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 2rem;
    }

    .payment-edit .info > dl {
        display: flex;
        flex-flow: column wrap;
        height: 4rem;
    }

    .payment-edit .info > dl * {
        margin-right: 1rem;
    }

</style>