<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input v-if="permissionCheck === true" class="field-amount" type="number" v-model="amount">

    <!-- TODO Show number instead of input field when amount is not changeable -->
    <span v-else>
        {{ amount }}
    </span>
</template>

<script>

import UserRights from '../../mixins/UserRights.js'

export default {
    mixins: [ 
        UserRights
    ],
    props: {
        rowId: Number
    },
    data: function() {
        return {
            amount: null
        }
    },
    watch: {
        amount: function(new_val) {
            this.$store.commit('setPaymentEditRowData', {
                idx: this.rowId,
                prop: 'paid_amount', 
                val: new_val
            })
        }
    }
}
</script>

<style>

    .field-amount {
        width: 7rem;
    }

</style>