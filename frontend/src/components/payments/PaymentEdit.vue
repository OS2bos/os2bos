<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div class="payment-edit">
        <dl>
            <dt>Betalt</dt>
            <dd>
                <span v-if="payment.paid">Ja</span>
                <span v-else>Nej</span>
            </dd>
            <template v-if="payment.paid_amount && payment.paid_date">
                <dt>Betalt beløb</dt>
                <dd>
                    {{ displayDigits(payment.paid_amount) }} kr.
                </dd>
                <dt>Betalt dato</dt>
                <dd>
                    {{ displayDate(payment.paid_date) }}
                </dd>
                <template v-if="payment.note">
                    <dt>Referencetekst</dt>
                    <dd>
                        {{ payment.note }}
                    </dd>
                </template>
            </template>
        </dl>
        <form @submit.prevent="prePayCheck()">
            <fieldset>
                <label for="field-amount" class="required">Betal beløb</label>
                <input type="number" step="0.01" v-model="paid.paid_amount" id="field-amount" required>

                <label for="field-date" class="required">Betal dato</label>
                <input type="date" v-model="paid.paid_date" id="field-date" required>

                <label for="field-note">Referencetekst</label>
                <input type="text" v-model="paid.note" id="field-note">
            </fieldset>

            <fieldset>
                <input type="submit" value="Betal" :disabled="paid.paid_amount && paid.paid_date ? false : true">
            </fieldset>
        </form>

        <!-- Submit payment modal -->
        <div v-if="showModal">
            <form @submit.prevent="pay()" class="modal-form">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div class="modal-container">

                            <div class="modal-header">
                                <slot name="header">
                                    <h2>Betaling</h2>
                                </slot>
                            </div>

                            <div class="modal-body">
                                <slot name="body">
                                    <p>
                                        Er du sikker på, at du vil sende {{ paid.paid_amount }} kr. til betaling?
                                    </p>
                                </slot>
                            </div>

                            <div class="modal-footer">
                                <slot name="footer">
                                    <button type="button" class="modal-cancel-btn" @click="reload()">Annullér</button>
                                    <button class="modal-confirm-btn" type="submit">Godkend</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import notify from '../notifications/Notify.js'
    import payment from '../../store-modules/payment.js'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'

    export default {
        
        data: function() {
            return {
                paid: {
                    paid_amount: null,
                    paid_date: null,
                    note: null
                },
                showModal: false
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        watch: {
            payment: function() {
                this.update()
            }
        },
        methods:{
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            update: function() {
                if (this.paid) {
                    this.paid = this.payment
                }
            },
            reload: function() {
                this.showModal = false
            },
            prePayCheck: function() {
                this.showModal = true
            },
            pay: function() {
                let data = {
                    paid_amount: this.paid.paid_amount,
                    paid_date: this.paid.paid_date,
                    note: this.paid.note
                }
                axios.patch(`/payments/${ this.payment.id }/`, data)
                .then(res => {
                    this.$router.push(`/payment/${ this.payment.id }`)
                    this.$store.dispatch('fetchPayment', res.data.id)
                    this.showModal = false
                    notify('Betaling godkendt', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            }
        },
        created: function() {
            this.update()
        }
    }

</script>

<style>

    .payment-edit {
        padding: 1rem 2rem;
        background-color: var(--grey1);
    }

    .payment-edit form {
        padding: 0;
    }

</style>