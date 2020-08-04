<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input v-if="visible" type="date" v-model="date">
    <span v-else>
        {{ displayPayDate(date) }}
    </span>
</template>

<script>

import PermissionLogic from '../../mixins/PermissionLogic.js'
import { json2jsDate } from '../../filters/Date.js'

export default {
    mixins: [ 
        PermissionLogic
    ],
    props: [
        'rowid',
        'compdata'
    ],
    computed: {
        date: {
            get: function() {
                return this.compdata.paid_date
            },
            set: function(new_val) {
                this.$store.commit('setPaymentEditRowData', {
                    idx: this.rowid,
                    prop: 'paid_date',
                    val: new_val
                })
            }
        },
        visible: function() {
            return this.is_payable(this.compdata)
        }
    },
    methods: {
        displayPayDate: function(payment) {
            return json2jsDate(payment)
        }
    }
}
</script>