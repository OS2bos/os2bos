<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
                
    <fieldset v-if="editable">
        <legend class="required">Skattekort</legend>
        
        <input 
            type="radio" 
            id="pay-method-detail-1"
            v-model="model"
            :value="1"
            name="pay-metho-detail"
            required>
        <label for="pay-method-detail-1">Hovedkort</label>

        <input 
            type="radio" 
            id="pay-method-detail-2"
            v-model="model"
            :value="2"
            name="pay-metho-detail"
            required>
        <label for="pay-method-detail-2">Bikort</label>

        <error :err-key="property" />

    </fieldset>

    <dl v-else>
        <dt>Skattekort</dt>
        <dd>{{ displayPaymentDetail(model) }}</dd>
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
    methods: {
        displayPaymentDetail: function(detail_id) {
            if (detail_id === 1) {
                return 'Hovedkort'
            } else if (detail_id === 2) {
                return 'Bikort'
            } else {
                return '-'
            }
        }
    },
    created: function() {
        this.property = 'payment_method_details'
    }
}    
</script>
