<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-amounts">
        
        <template v-if="p.payment_type === 'ONE_TIME_PAYMENT' || p.payment_type === 'RUNNING_PAYMENT'">

            <label class="required" for="field-amount-1">Beløb</label>
            <input v-model="p.payment_amount" type="number" step="0.01" required id="field-amount-1"> kr.
            
            <error err-key="payment_amount" />

        </template>

        <template v-if="p.payment_type === 'PER_HOUR_PAYMENT' || p.payment_type === 'PER_DAY_PAYMENT' || p.payment_type === 'PER_KM_PAYMENT'" class="rows">

            <div style="margin-right: .5rem;">
                <label class="required" for="field-amount-2" v-if="p.payment_type === 'PER_HOUR_PAYMENT'">betales antal timer</label>
                <label class="required" for="field-amount-2" v-if="p.payment_type === 'PER_DAY_PAYMENT'">betales antal døgn</label>
                <label class="required" for="field-amount-2" v-if="p.payment_type === 'PER_KM_PAYMENT'">betales antal kilometer</label>
                <input v-model="p.payment_units" type="number" step="0.01" required id="field-amount-2">
                
                <error err-key="payment_units" />
            </div>
            <div>
                <label class="required" for="field-rate">til takst</label>
                <input v-model="p.payment_amount" type="number" step="0.01" required id="field-rate"> kr.

                <error err-key="payment_amount" />
            </div>

        </template>

        <p style="margin-top: .75rem;">
            <a href="https://www.kl.dk/media/16653/taksttabel_-2019.pdf" target="_blank">Find takster her</a>
        </p>

    </fieldset>

</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        props: [
            'pay'
        ],
        data: function() {
            return {
                p: {
                    payment_type: 'RUNNING_PAYMENT', // default is running payment
                    payment_frequency: 'MONTHLY', // default is pr month
                    payment_units: 0,
                    payment_amount: 0
                }
            }
        },
        watch: {
            pay: function() {
                this.p = this.pay
            },
            p: {
                handler (newVal) {
                    this.$emit('update', this.p)
                },
                deep: true
            }
        },
        created: function() {
            if (this.pay) {
                this.p = this.pay
            }
        }

    }
    
</script>

<style>

    .payment-amount {
        padding: 0 1rem 1rem;
    }

    .payment-amount .payment-amount-types,
    .payment-amount .payment-amount-fields {
        margin: 1rem;
    }

</style>