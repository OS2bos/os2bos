<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input v-if="visible" class="field-amount" type="number" v-model="amount">
    <span v-else class="amount-paid">
        {{ displayDigits(amount) }} kr.
    </span>
</template>

<script>

import PermissionLogic from '../../mixins/PermissionLogic.js'
import { cost2da } from '../../filters/Numbers.js'

export default {
    mixins: [ 
        PermissionLogic
    ],
    props: [
        'rowid',
        'compdata'
    ],
    computed: {
        amount: {
            get: function() {
                if (this.compdata.paid_amount) {
                    return this.compdata.paid_amount
                } else {
                    return false
                }
            }, 
            set: function(new_val) {
                let new_data = Object.assign({}, this.compdata)
                new_data.paid_amount = new_val
                this.$emit('update', {operation: 'update', data: new_data})
            }   
        },
        visible: function() {
            return this.is_payable(this.compdata)
        }
    },
    methods: {
        displayDigits: function(num) {
            return cost2da(num)
        }
    }
}
</script>