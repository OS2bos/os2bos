<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input v-if="permissionCheck === true && isPayableManually" class="field-amount" type="number" v-model="amount">

    <span v-else>
        {{  displayDigits(amount) }} kr.
    </span>
</template>

<script>

import UserRights from '../../mixins/UserRights.js'
import IsPayableManually from '../../mixins/IsPayableManually'
import { cost2da } from '../../filters/Numbers.js'

export default {
    mixins: [ 
        UserRights,
        IsPayableManually
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
    },
    methods: {
        displayDigits: function(num) {
            return cost2da(num)
        },
    },
    created: function() {
        this.amount = this.payments.filter(p => {
            return p.id === this.rowId
        })[0].paid_amount
    }
}
</script>