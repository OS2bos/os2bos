<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input type="date" v-model="date">
    <!-- TODO Show date instead of input field when amount is not changeable -->
</template>

<script>
export default {
    props: {
        rowId: Number
    },
    data: function() {
        return {
            date: null
        }
    },
    watch: {
        date: function(new_val) {
            this.$store.commit('setPaymentEditRowData', {
                idx: this.rowId,
                prop: 'paid_date', 
                val: new_val
            })
        }
    }
}
</script>