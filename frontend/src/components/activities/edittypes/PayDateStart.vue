<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <fieldset v-if="editable">
        <label for="pay-date-start" class="required">Startdato</label>
        <p v-if="startDateSet && act.activity_type !== 'MAIN_ACTIVITY'">
            Tidligst {{ displayDate(startDateSet) }}
        </p>
        <input 
            type="date" 
            v-model="model" 
            id="pay-date-start"
            :max="endDateSet"
            :min="startDateSet" 
            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
            placeholder="åååå-mm-dd"
            required>
        <error :err-key="property" />
    </fieldset>
    
    <dl v-else>
        <dt>Startdato</dt>
        <dd>{{ displayDate(model) }}</dd>
    </dl>

</template>

<script>
import mixin from '../../mixins/ActivityEditMixin.js'
import datemixin from '../../mixins/ActivityDateEditMixin.js'
import Error from '../../forms/Error.vue'

export default {
    components: {
        Error
    },
    mixins: [
        mixin,
        datemixin
    ],
    created: function() {
        this.property = 'start_date'
    }
}
</script>