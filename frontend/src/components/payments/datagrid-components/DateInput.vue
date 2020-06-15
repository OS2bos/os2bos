<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input v-if="permissionCheck === true && isPayableManually" type="date" v-model="date">

    <span v-else>
        {{ displayPayDate(date) }}
    </span>
</template>

<script>

import UserRights from '../../mixins/UserRights.js'
import IsPayableManually from '../../mixins/IsPayableManually'
import { json2jsDate } from '../../filters/Date.js'

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
    },
    methods: {
        displayPayDate: function(payment) {
            return json2jsDate(payment)
        }
    },
    created: function() {
        this.date = this.payments.filter(p => {
            return p.id === this.rowId
        })[0].paid_date
    }
}
</script>