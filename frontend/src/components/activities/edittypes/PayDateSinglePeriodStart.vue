<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div v-if="editable" style="margin-right: 1rem;">
        <label for="pay-date-start-period">Fra</label>
        <input 
            type="date" 
            v-model="model" 
            id="pay-date-start-period"
            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
            placeholder="åååå-mm-dd">
        <error :err-key="property" />
    </div>

</template>

<script>
import mixin from '../../mixins/ActivityEditMixin.js'
import Error from '../../forms/Error.vue'

export default {
    components: {
        Error
    },
    mixins: [
        mixin
    ],
    created: function() {
        this.property = 'start_date'
    }
}
</script>