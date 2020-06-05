<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <button v-if="permissionCheck === true" type="button" @click="submitHandler">Gem</button>
</template>

<script>
import axios from '../../http/Http.js'
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
            date: null,
            amount: null
        }
    },
    computed: {
        row_data: function() {
            return this.$store.getters.getPayments
        },
        disabled: function() {
            // TODO Update this boolean to set the SAVE button disabled when no values are entered
            return false
        }
    },
    watch: {
        row_data: function() {
            let payment = this.row_data.results.filter(p => {
                return p.id === this.rowId
            })
            console.log(payment)
            this.date = payment.paid_date
            this.amount = payment.paid_amount
        }
    },
    methods: {
        submitHandler: function() {
            
            // TODO Submit values from input fields in same row. 
            // Get values from current state.payments and use this.rowId to identify the correct payment
            
        }
    }
}
</script>