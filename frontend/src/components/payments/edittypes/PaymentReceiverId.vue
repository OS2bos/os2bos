<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
                
    <fieldset v-if="editable">
        <label for="pay-receiver-id" :class="{required: payment_plan.recipient_type !== 'INTERNAL'}">
            {{ id_str }}
        </label>
        <input type="text" id="pay-receiver-id" v-model="model" :required="payment_plan.recipient_type !== 'INTERNAL'">
        <error :err-key="property" />
    </fieldset>

    <dl v-else>
        <dt>
            {{ id_str }}
        </dt>
        <dd>{{ model }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'
import Error from '../../forms/Error.vue' 

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    computed: {
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        },
        id_str: function() {
            if (this.payment_plan.recipient_type === 'PERSON') {
                return 'CPR-nr'
            } else if (this.payment_plan.recipient_type === 'COMPANY') {
                return 'CVR-nr'
            } else if (this.payment_plan.recipient_type === 'INTERNAL') {
                return 'Reference'
            } else {
                return 'ID'
            }
        }
    },
    created: function() {
        this.property = 'recipient_id'
    }
}    
</script>
