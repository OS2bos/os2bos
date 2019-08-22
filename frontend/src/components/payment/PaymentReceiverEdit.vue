<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="payment-receiver">
        <label class="required">Betalingsmodtager</label>
        <select v-model="entry.recipient_type" required>
            <option value="INTERNAL">Intern</option>
            <option value="COMPANY">Firma</option>
            <option value="PERSON">Person</option>
        </select>
        <error err-key="recipient_type" />
        <fieldset v-if="entry.recipient_type === 'COMPANY' && service_providers">
            <label>Mulige leverandører</label>
            <select v-model="service_provider">
                <option v-for="s in service_providers" :key="s.id" :value="s">
                    {{ s.name }}
                </option>
            </select>
        </fieldset>

        <template v-if="entry.recipient_type">
            <fieldset>
                <label class="required" v-if="entry.recipient_type === 'INTERNAL'" for="field-payee-id">
                    Reference
                </label>
                <label class="required" v-if="entry.recipient_type === 'COMPANY'" for="field-payee-id">
                    CVR-nr
                </label>
                <label class="required" v-if="entry.recipient_type === 'PERSON'" for="field-payee-id">
                    CPR-nr
                </label>
                <input type="text" id="field-payee-id" v-model="entry.recipient_id" required>
                <error err-key="recipient_id" />
            </fieldset>
            <fieldset>
                <label class="required" for="field-payee-name">Navn</label>
                <input type="text" id="field-payee-name" v-model="entry.recipient_name" required>
                <error err-key="recipient_name" />
            </fieldset>
        </template>
    </section>
</template>

<script>

    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
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
        margin: 1rem 0;
    }

</style>