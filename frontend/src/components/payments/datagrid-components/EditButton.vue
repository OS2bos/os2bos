<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div>
        <button type="button" @click="openEditDiag" class="datagrid-action-btn" style="min-width: 9rem;">
            Betaling #{{ compdata.id }}
        </button>
        <payment-edit-diag v-if="edit_diag_open" :payment="compdata" @closedialog="closeEditDiag" />
    </div>

</template>

<script>
import PaymentEditDiag from '../payment-editing/PaymentEdit.vue'

export default {
    components: {
        PaymentEditDiag
    },
    props: [
        'rowid',
        'compdata'
    ],
    data: function() {
        return {
            edit_diag_open: false
        }
    },
    methods: {
        openEditDiag: function() {
            this.edit_diag_open = true
        },
        closeEditDiag: function() {
            this.edit_diag_open = false
        }
    }
}
</script>