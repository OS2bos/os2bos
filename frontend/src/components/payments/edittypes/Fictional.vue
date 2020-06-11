<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <fieldset v-if="editable">
        <input type="checkbox" v-model="model" id="pay-fictional">
        <label for="pay-fictional">Fiktiv betaling</label>
    </fieldset>

    <p v-else class="field-fictional-noedit" style="margin: 0;">
        <strong v-if="model === true">
            Dette er en fiktiv betaling
        </strong>
    </p>
</template>

<script>
import mixin from '../../mixins/PaymentPlanEditMixin.js'

export default {
    mixins: [
        mixin
    ],
    created: function() {
        this.property = 'fictive'
    }
}
</script>