<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <button v-if="visible" type="button" @click="submitHandler()" :disabled="disabled">
        {{buttonTxt}}
    </button>
</template>

<script>
import axios from '../../http/Http.js'
import PermissionLogic from '../../mixins/PermissionLogic.js'
import notify from '../../notifications/Notify.js'
import { epoch2DateStr } from '../../filters/Date.js'

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
        disabled: function() {
            if (this.compdata.paid_amount && this.compdata.paid_date) {
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
        update: function() {
            this.$emit('update')
        },
        submitHandler: function() {
            let data = {
                    paid_amount: this.compdata.paid_amount,
                    paid_date: this.compdata.paid_date,
                    note: this.compdata.note ? this.compdata.note : '',
                    paid: true
            }
            if (this.user.profile === 'workflow_engine' && this.compdata.paid) {
                // TODO: Clear up what this is actually for
                axios.get(`/editing_past_payments_allowed/`)
                .then(res => {
                    this.patchPayments(data)
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            } else {
                this.patchPayments(data)        
            }
        },
        patchPayments: function(data) {
            axios.patch(`/payments/${ this.rowid }/`, data)
            .then(res => {
                this.buttonTxt = 'Gemt'
                notify('Betaling registreret', 'success')
                this.update()
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        }  
    }
}
</script>