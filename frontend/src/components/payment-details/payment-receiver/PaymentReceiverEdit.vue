<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="payment-payee">
                    
        <fieldset>
            <legend>Hvem skal betales?</legend>

            <label class="required" for="field-payee">Betalingsmodtager</label>
            <select v-model="p_recipient_type" required id="field-payee" ref="recipientselect">
                <option value="INTERNAL">Intern</option>
                <option value="COMPANY">Firma</option>
                <option value="PERSON">Person</option>
            </select>
            <error err-key="recipient_type" />

        </fieldset>

        <payee-company v-if="p_recipient_type === 'COMPANY'" />
        <payee-internal v-if="p_recipient_type === 'INTERNAL'" />
        <payee-person v-if="p_recipient_type === 'PERSON'" />

    </div>

</template>

<script>

    import Error from '../../forms/Error.vue'    
    import PayeeCompany from './CompanyEdit.vue'
    import PayeeInternal from './InternalEdit.vue'
    import PayeePerson from './PersonEdit.vue'

    export default {

        components: {
            Error,
            PayeeCompany,
            PayeeInternal,
            PayeePerson
        },
        data: function() {
            return {
                p_recipient_type: null
            }
        },
        computed: {
            recipient_type: function() {
                return this.$store.getters.getPaymentRecipientType
            }
        },
        watch: {
            p_recipient_type: function() {
                this.$store.commit('setPaymentRecipientType', this.p_recipient_type)
            }
        },
        mounted: function() {
            // Update p_recipient_type
            if (this.recipient_type) {
                this.p_recipient_type = this.recipient_type
            }

            // Add eventlistener after mounted, so only user can wipe fields when changing type
            this.$refs.recipientselect.addEventListener('change', ev => {
                console.log('change it now', ev)
                this.$store.commit('setPaymentRecipientId', null)
                this.$store.commit('setPaymentRecipientName', null)
            })
        }

    }
    
</script>
