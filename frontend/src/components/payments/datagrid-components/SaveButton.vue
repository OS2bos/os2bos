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
        save: function() {
            this.$emit('update', {operation: 'save', data: this.compdata})
            this.buttonTxt = 'Gemt'
        }
    }
}
</script>