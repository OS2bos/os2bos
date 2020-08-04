<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div class="payment modal-container">

        <div class="modal-header">
            <h2>
                <span class="payment-title">
                    <span v-if="payment.paid" class="label label-GRANTED" title="Betalt">
                        <i class="material-icons" style="width: 1.5rem;">checkmark</i>
                    </span>
                    Betaling #{{ payment.id }}
                    <span v-if="payment.payment_schedule__fictive" class="dim">(Fiktiv)</span>
                    <span v-if="payment.paid_amount" class="dim">(Betalt)</span>
                </span>
            </h2>
                        
        </div>

        <div class="modal-body">
            
            <div class="row">

                <dl class="info" style="width: 50%;">
                    <dt>Ydelse</dt>
                    <dd v-if="payment.activity__id">
                        <a @click="navToLink(`/activity/${ payment.activity__id }`)" v-html="activityId2name(payment.activity__details__id)"></a>
                    </dd>
                    <dt>Betalingsnøgle</dt>
                    <dd>{{ payment.payment_schedule__payment_id }}</dd>
                    <dt>Beløb, planlagt</dt>
                    <dd class="dim">{{ displayDigits(payment.amount) }} kr.</dd>
                    <dt>Betalingsdato, planlagt</dt>
                    <dd class="dim">{{ displayDate(payment.date) }}</dd>
                    <dt>Kontostreng</dt>
                    <dd>{{ payment.account_string ? payment.account_string : 'ukendt' }}</dd>
                    <dt>Kontoalias</dt>
                    <dd>{{ payment.account_alias ? payment.account_alias : 'ukendt' }}</dd>
                    <template v-if="payment.payment_schedule__fictive">
                        <dt>Betaling</dt>
                        <dd>Fiktiv</dd>
                    </template>
                </dl>

                <div class="payment-edit" style="width: 50%;">
                    <dl v-if="paymentlock">
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
                    </dl>
                    <template v-if="permissionCheck === true && this.payment.activity__status === 'GRANTED'">
                        <form @submit.prevent="prePayCheck()" v-if="!paymentlock && payment.is_payable_manually">
                            <error />
                            <fieldset>
                                <label for="field-amount" class="required">Betal beløb</label>
                                <input type="number" step="0.01" v-model="paid.paid_amount" id="field-amount" required>

                                <label for="field-date" class="required">Betal dato</label>
                                <input type="date" v-model="paid.paid_date" id="field-date" required>

                                <label for="field-note">Referencetekst</label>
                                <input type="text" v-model="paid.note" id="field-note">
                                <error err-key="note" />
                            </fieldset>
                        </form>
                    </template>
                </div>

            </div>

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

        <div class="modal-footer">
            
            <button v-if="!paymentlock && this.payment.activity__status === 'GRANTED'" type="button" :disabled="paid.paid_amount && paid.paid_date ? false : true" @click="pay()">Betal</button>
            <button type="button" class="modal-cancel-btn" @click="closeDiag()">Luk</button>
        
        </div>

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import Error from '../forms/Error.vue'
    import UserRights from '../mixins/UserRights.js'
    import notify from '../notifications/Notify.js'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name } from '../filters/Labels.js'

    export default {

        components: {
            Error
        },
        mixins: [
            UserRights
        ],
        data: function() {
            return {
                paid: {
                    paid_amount: null,
                    paid_date: null,
                    note: null
                },
                showModal: false,
                paymentlock: true
            }
        },
        computed: {
            p_id: function() {
                return this.$route.params.payId
            },
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        watch: {
            p_id: function() {
                this.update()
            },
            payment: function() {
                        if (!this.payment.paid_amount && !this.payment.paid_date && this.payment.is_payable_manually) {
                            this.paymentlock = false
                            this.paid.paid_amount = this.payment.amount
                            this.paid.paid_date = this.payment.date
                        } else {
                            this.paymentlock = true
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
            update: function() {
                this.$store.dispatch('fetchPayment', this.p_id)
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
                    note: this.paid.note ? this.paid.note : '',
                    paid: true
                }
                axios.patch(`/payments/${ this.payment.id }/`, data)
                .then(res => {
                    this.showModal = false
                    notify('Betaling godkendt', 'success')
                    this.$emit('closepaymentdiag')
                    this.update()
                    this.$emit('update')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            },
            closeDiag: function() {
                this.$emit('close')
            },
            navToLink: function(path) {
                this.$emit('close')
                this.$router.push(path)
            }
        },
        created: function() {
            this.update()
        }

    }

</script>

<style>

    .payment {
        padding: 2rem;
        margin: 2rem auto;
    }

    .payment.modal-container {
        padding: 2rem;
        width: 35rem;
        max-width: 90vw;
    }

    .payment .modal-footer {
        text-align: right;
    }

    .payment .modal-header > h2 {
        padding: 0;
    }
    
    .payment .modal-body {
        margin: 1rem 0;
    }

    .payment a {
        cursor: pointer;
    }

    .payment .payment-title-link:hover,
    .payment .payment-title-link:active {
        color: var(--grey10);
    }

    .payment .payment-title {
        margin-top: 1rem;
        display: block;
    }

    .payment .is-paid {
        float: right;
        font-size: 1rem;
    }

</style>