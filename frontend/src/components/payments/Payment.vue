<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div class="payment">
        <nav class="payment-nav" v-if="payment.activity__details__id">
            <router-link :to="`/activity/${ payment.activity__id }`">
                <i class="material-icons">arrow_upward</i>
                {{ activityId2name(payment.activity__details__id) }}
            </router-link>
        </nav>
        <h1>
            Betaling #{{ payment.id }}
            <span v-if="payment.paid" class="dim">- betalt</span>
        </h1>

        <div class="row">
            <router-link :to="`/payment/${ payment.id }/edit/`"></router-link>
            <dl class="info">
                <dt>Betalingsnøgle</dt>
                <dd>{{ payment.payment_schedule__payment_id }}</dd>
                
                <dt>Beløb, planlagt</dt>
                <dd class="dim">{{ displayDigits(payment.amount) }} kr.</dd>
                <dt>Betalingsdato, planlagt</dt>
                <dd class="dim">{{ displayDate(payment.date) }}</dd>
                <dt>Kontostreng</dt>
                <dd>{{ payment.account_string }}</dd>
            </dl>

            <payment-edit />

        </div>


    </div>

</template>

<script>

    import PaymentEdit from './PaymentEdit.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name } from '../filters/Labels.js'

    export default {
        
        components: {
            PaymentEdit
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
                if (this.payment) {
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/payments',
                            title: 'Betalinger'
                        },
                        {
                            link: false,
                            title: `Betaling ${ this.p_id }`
                        }
                    ])
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

    .payment .payment-nav {
        background-color: var(--grey1);
    }

    .payment .payment-nav > a {
        border-bottom: none;
        padding: .5rem 1rem;
        display: block;
    }

    .payment .info {
        padding: 0rem 1rem;
    }

</style>