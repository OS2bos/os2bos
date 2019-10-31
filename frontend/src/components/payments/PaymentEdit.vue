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
            <template v-if="payment.paid || payment.automatic">
                <dt>Beløb</dt>
                <dd>
                    (Faktisk betalt beløb)
                </dd>
                <dt>Dato</dt>
                <dd>
                    (Faktisk betalingsdato)
                </dd>
            </template>
        </dl>
        <template v-if="permissionCheck === true">
            <form @submit.prevent="prePayCheck()" v-if="!payment.paid && !payment.automatic">
                <fieldset>
                
                    <label for="field-amount" class="required">Betal beløb</label>
                    <input type="number" step="0.01" v-model="paid_amount" id="field-amount" required>
                    
                    <label for="field-date" class="required">Betal dato</label>
                    <input type="date" v-model="paid_date" id="field-date" required>

                    <label for="field-note">Referencetekst</label>
                    <input type="text" v-model="paid_note" id="field-note">

                </fieldset>
                <fieldset>
                    <input type="submit" value="Betal" :disabled="paid_amount && paid_date ? false : true">
                </fieldset>
            </form>
        </template>

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
                                        Er du sikker på, at du vil sende {{ paid_amount }} kr. til betaling?
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
    import UserRights from '../mixins/UserRights.js'

    export default {

        mixins: [UserRights],
        
        data: function() {
            return {
                paid_amount: null,
                paid_date: null,
                paid_note: null,
                showModal: false
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        methods:{
            reload: function() {
                this.showModal = false
            },
            prePayCheck: function() {
                this.showModal = true
            },
            pay: function() {
                let data = {
                    paid_amount: this.paid_amount,
                    paid_date: this.paid_date,
                    note: this.paid_note
                }
                axios.patch(`/payments/${ this.payment.id }/`, data)
                .then(res => {
                    this.$store.dispatch('fetchPayment', res.data.id)
                    this.$router.push(`/payments/`)
                    this.showModal = false
                    notify('Betaling godkendt', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            }
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