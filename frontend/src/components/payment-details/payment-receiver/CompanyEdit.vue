<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <fieldset class="payment-payee-company" style="margin-top: 1rem;">

        <p>Betales via faktura</p>

        <template v-if="service_providers">
            <label>Mulige leverandører</label>
            <select v-model="service_provider">
                <option v-for="s in service_providers" :key="s.id" :value="s">
                    {{ s.name }}
                </option>
            </select>
        </template>

        <label class="required" for="field-payee-id">CVR-nr</label>
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
                p_recipient_name: null,
                service_provider: null
            }
        },
        computed: {
            activity_detail: function() {
                return this.$store.getters.getActivityDetail
            },
            service_providers_data: function() {
                return this.$store.getters.getServiceProviders
            },
            service_providers: function() {
                if (this.activity_detail) {
                    let arr = []
                    for (let s in this.activity_detail.service_providers) {
                        let sp = this.service_providers_data.find(function(element) {
                            return element.id = this.activity_detail.service_providers[s].id
                        })
                        arr.push(sp)
                    }
                    if (arr.length > 0) {
                        return arr
                    } else {
                        return this.service_providers_data
                    }
                } else {
                    return false
                }
            },
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
            },
            service_provider: function() {
                this.p_recipient_id = this.service_provider.cvr_number
                this.p_recipient_name = this.service_provider.name
            },
        }, 
        methods: {
            commitData: function() {
                this.$store.commit('setPaymentMethod', 'INVOICE')
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