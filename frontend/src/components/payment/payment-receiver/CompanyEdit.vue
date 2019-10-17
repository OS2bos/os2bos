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
                },
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
            }
        },
        watch: {
            pay: function() {
                this.p = this.pay
            },
            p: {
                handler () {
                    this.p.payment_method = 'INVOICE'
                    this.$emit('update', this.p)
                },
                deep: true
            },
            service_provider: function() {
                this.p.recipient_id = this.service_provider.cvr_number
                this.p.recipient_name = this.service_provider.name
            }
        },
        created: function() {
            if (this.pay) {
                this.p = this.pay
            }
        }

    }

</script>