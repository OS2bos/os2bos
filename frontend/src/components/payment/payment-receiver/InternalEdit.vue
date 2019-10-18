<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <fieldset class="payment-payee-internal" style="margin-top: 1rem;">

        <p>Betales ved intern afregning</p>

        <label class="required" for="field-payee-id">Reference</label>
        <input type="text" id="field-payee-id" v-model="p.recipient_id" required>
        <error err-key="recipient_id" />

        <label class="required" for="field-payee-name">Navn</label>
        <input type="text" id="field-payee-name" v-model="p.recipient_name" required>
        <error err-key="recipient_name" />

    </fieldset>
</template>

<script>

    import Error from '../../forms/Error.vue'

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
                    recipient_id: null,
                    recipient_name: null
                }
            }
        },
        watch: {
            payee: function() {
                this.p = this.pay
            },
            p: {
                handler () {
                    this.p.payment_method = 'INTERNAL'
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