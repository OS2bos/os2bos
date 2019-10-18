<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <fieldset class="payment-payee-internal" style="margin-top: 1rem;">

        <p><strong>Betales ved intern afregning</strong></p>

        <label class="required" for="field-payee-id">Reference</label>
        <input type="text" id="field-payee-id" v-model="p_recipient_id" required>
        <error err-key="recipient_id" />

        <label class="required" for="field-payee-name">Navn</label>
        <input type="text" id="field-payee-name" v-model="p_recipient_name" required>
        <error err-key="recipient_name" />

    </fieldset>
    
</template>

<script>

    import Error from '../../forms/Error.vue'

    export default {

        components: {
            Error
        },
        data: function() {
            return {
                p_recipient_id: null,
                p_recipient_name: null
            }
        },
        computed: {
            recipient_id: function() {
                return this.$store.getters.getPaymentRecipientId
            },
            recipient_name: function() {
                return this.$store.getters.getPaymentRecipientName
            }
        },
        watch: {
            recipient_id: function() {
                this.p_recipient_id = this.recipient_id
            },
            recipient_name: function() {
                this.p_recipient_name = this.recipient_name
            },
            p_recipient_id: function() {
                this.$store.commit('setPaymentRecipientId', this.p_recipient_id)
                this.commitData()
            },
            p_recipient_name: function() {
                this.$store.commit('setPaymentRecipientName', this.p_recipient_name)
                this.commitData()
            }
        },
        methods: {
            commitData: function() {
                this.$store.commit('setPaymentMethod', 'INTERNAL')
            }
        },
        created: function() {
            if (this.recipient_id) {
                this.p_recipient_id = this.recipient_id
            }
            if (this.recipient_name) {
                this.p_recipient_name = this.recipient_name
            }
        }

    }

</script>