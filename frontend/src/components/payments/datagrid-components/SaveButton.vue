<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <button v-if="visible" type="button" @click="save" :disabled="disabled">
        {{ buttonTxt }}
    </button>
</template>

<script>
import PermissionLogic from '../../mixins/PermissionLogic.js'

export default {
    mixins: [ 
        PermissionLogic
    ],
    props: [
        'rowid',
        'compdata'
    ],
    data: function() {
        return {
            buttonTxt: 'Gem'
        }
    },
    computed: {
        editpayment: function() {
            return this.$store.getters.getEditedPayment(this.compdata.id)
        },
        disabled: function() {
            if (this.editpayment && this.editpayment.paid_amount && this.editpayment.paid_date) {
                return false
            } else {
                return true
            }
        }, 
        visible: function() {
            return this.is_payable(this.compdata)
        }
    },
    methods: {
        save: function() {
            this.$store.dispatch('saveEditedPayment', this.compdata.id)
        },
        update: function(new_data) {
            this.$emit('update', new_data)
        },
        submitHandler: function() {
            let data = {
                    paid_amount: this.compdata.paid_amount,
                    paid_date: this.compdata.paid_date,
                    note: this.compdata.note ? this.compdata.note : '',
                    paid: true
            }
            this.patchPayments(data)
        },
        patchPayments: function(data) {
            axios.patch(`/payments/${ this.rowid }/`, data)
            .then(res => {
                this.buttonTxt = 'Gemt'
                this.$emit('update', res)
            })
        }
    }
}
</script>