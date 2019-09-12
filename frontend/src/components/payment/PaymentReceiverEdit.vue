<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <fieldset class="payment-receiver">
        <legend>Hvem skal have betaling?</legend>
        <label class="required" for="field-payee">Betalingsmodtager</label>
        <select v-model="entry.recipient_type" required id="field-payee">
            <option value="INTERNAL">Intern</option>
            <option value="COMPANY">Firma</option>
            <option value="PERSON">Person</option>
        </select>
        <error err-key="recipient_type" />

        <template v-if="entry.recipient_type === 'COMPANY' && service_providers">
            <label>Mulige leverandører</label>
            <select v-model="service_provider">
                <option v-for="s in service_providers" :key="s.id" :value="s">
                    {{ s.name }}
                </option>
            </select>
        </template>

        <template v-if="entry.recipient_type">
            
            <label class="required" v-if="entry.recipient_type === 'INTERNAL'" for="field-payee-id">
                Reference
            </label>
            <label class="required" v-if="entry.recipient_type === 'COMPANY'" for="field-payee-id">
                CVR-nr
            </label>
            <input v-if="entry.recipient_type !== 'PERSON'" type="text" id="field-payee-id" v-model="entry.recipient_id" required>
            
            <cpr-lookup v-if="entry.recipient_type === 'PERSON'" :cpr.sync="entry.recipient_id" :name.sync="entry.recipient_name" />
            
            <error err-key="recipient_id" />
        
            <template v-if="entry.recipient_type !== 'PERSON'">
                <label class="required" for="field-payee-name">Navn</label>
                <input type="text" id="field-payee-name" v-model="entry.recipient_name" required>
                <error err-key="recipient_name" />
            </template>
        </template>
    </fieldset>
</template>

<script>

    import Error from '../forms/Error.vue'
    import CprLookup from '../forms/CprLookUp.vue'

    export default {

        components: {
            Error,
            CprLookup
        },
        props: [
            'paymentObj'
        ],
        data: function() {
            return {
                entry: {
                    recipient_type: null,
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
            paymentObj: function() {
                this.entry = this.paymentObj
            },
            entry: {
                handler () {
                    this.$emit('update', this.entry)
                },
                deep: true
            },
            service_provider: function() {
                this.entry.recipient_id = this.service_provider.cvr_number
                this.entry.recipient_name = this.service_provider.name
            }
        },
        created: function() {
            if (this.paymentObj) {
                this.entry = this.paymentObj
            }
        }

    }
</script>

<style>

    .payment-receiver {
        
    }

</style>