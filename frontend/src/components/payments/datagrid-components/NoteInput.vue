<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <input v-if="visible" class="field-note" type="text" v-model="note">
    <span v-else>
        {{ note }}
    </span>
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
    computed: {
        note: {
            get: function() {
                return this.compdata.note
            },
            set: function(new_val) {
                this.$store.commit('setPaymentEditRowData', {
                    idx: this.rowid,
                    prop: 'note', 
                    val: new_val
                })
            }
        },
        visible: function() {
            return this.is_payable(this.compdata)
        }
    }
}
</script>