<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section>
        <h3>Priser</h3>
        <ol>
            <li v-for="p in prices" :key="p.start_date">
                {{ p }}
            </li>
        </ol>
    </section>

</template>

<script>
export default {
    computed: {
        prices: function() {
            return this.$store.getters.getPaymentPlanProperty('prices_per_unit')
        }
    }
}
</script>