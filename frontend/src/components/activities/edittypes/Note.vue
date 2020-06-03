<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">
        <label for="note">Supplerende oplysninger</label>
        <textarea v-model="model" id="note"></textarea>
        <error :err-key="this.property" />
    </fieldset>

    <dl v-else>
        <dt>Supplerende oplysninger</dt>
        <dd>{{ model ? model : '-' }}</dd>
    </dl>

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
        this.property = 'note'
    }
}
</script>