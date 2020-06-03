<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
                
    <fieldset v-if="editable">
        <label for="pay-receiver-name" class="required">
            Navn
        </label>
        <input type="text" id="pay-receiver-name" v-model="model" required>
        <error :err-key="property" />
    </fieldset>

    <dl v-else>
        <dt>Navn</dt>
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
    created: function() {
        this.property = 'recipient_name'
    }
}    
</script>
