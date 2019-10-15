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
        <form @submit.prevent="pay()" v-if="!payment.paid && !payment.automatic">
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

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import notify from '../notifications/Notify.js'

    export default {
        
        data: function() {
            return {
                paid_amount: null,
                paid_date: null,
                paid_note: null
            }
        },
        computed: {
            payment: function() {
                return this.$store.getters.getPayment
            }
        },
        methods:{
            pay: function() {
                if (confirm(`Er du sikker på, at du vil sende ${ this.paid_amount } kr til betaling?`)) {
                    
                    this.$store.dispatch('updatePayment', data)

                }
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