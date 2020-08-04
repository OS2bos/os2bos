<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <dl>
        <dt>Betaling dækker periode</dt>
        <dd>{{ period_start }} - {{ period_end }}</dd>
    </dl>

</template>

<script>
import { json2jsDate } from '../../filters/Date.js'

export default {
    computed: {
        period_start: function() {
            return json2jsDate( this.$store.getters.getActivityProperty('start_date') )
        },
        period_end: function() {
            return json2jsDate( this.$store.getters.getActivityProperty('end_date') )
        }
    }
}
</script>