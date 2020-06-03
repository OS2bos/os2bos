<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template v-if="model === 'COMPANY'">
    <fieldset>
        <label for="field-select-company">Mulige leverandører</label>
        <select v-model="service_provider" id="field-select-company">
            <option v-for="s in service_providers" :key="s.id" :value="s" :title="s.name">
                {{ truncateName(s.name) }}
            </option>
        </select>
    </fieldset>
</template>

<script>
export default {
    data: function() {
        return {
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
        service_provider: function(new_obj) {
            this.$store.commit('setPaymentPlanProperty', { 
                prop: 'recipient_name',
                val: new_obj.name
            })
            this.$store.commit('setPaymentPlanProperty', { 
                prop: 'recipient_id',
                val: new_obj.cvr_number
            })
            this.$store.commit('setPaymentPlanProperty', { 
                prop: 'payment_method',
                val: 'INVOICE'
            })
        }
    },
    methods: {
        truncateName: function(str) {
            if (str.length > 30) {
                return str.substr(0,25) + '...'
            } else {
                return str
            }
        }
    }
}
</script>