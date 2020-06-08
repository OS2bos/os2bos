<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <button v-if="permissionCheck === true && isPayableManually" type="button" @click="submitHandler()">{{buttonTxt}}</button>
</template>

<script>
import axios from '../../http/Http.js'
import UserRights from '../../mixins/UserRights.js'
import IsPayableManually from '../../mixins/IsPayableManually'
import notify from '../../notifications/Notify.js'

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
            buttonTxt: 'Gem'
        }
    },
    computed: {
        disabled: function() {
            // TODO Update this boolean to set the SAVE button disabled when no values are entered
        }
    },
    methods: {
        update: function() {
            this.$store.dispatch('fetchPayments', this.$route.query)
        },
        submitHandler: function() {
            let payment = this.payments.find(p => {
                return p.id === this.rowId
            })
            let data = {
                    paid_amount: payment.paid_amount,
                    paid_date: payment.paid_date,
                    note: payment.note ? payment.note : '',
                    paid: true
            }
            axios.patch(`/payments/${ this.rowId }/`, data)
            .then(res => {
                this.buttonTxt = 'Gemt'
                notify('Betaling godkendt', 'success')
                this.update()
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        }
    }
}
</script>