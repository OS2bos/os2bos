<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <dl>
        <dt>Type</dt>
        <dd>{{ displayActType(act.activity_type) }}</dd>
    </dl>
</template>

<script>
import { displayActivityType } from '../../filters/Labels.js'

export default {
    computed: {
        act: function() {
            return this.$store.getters.getActivity
        }
    },
    methods: {
        displayActType(type) {
            return displayActivityType(type)
        }
    }
}
</script>