<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div>
        <button type="button" @click="openEditDiag" class="datagrid-action-expandable" style="min-width: 9rem;">
            <i class="material-icons">launch</i>
            # {{ compdata.id }}
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

<style>

.datagrid-action-expandable {
    border: none; 
    background-color: transparent;
    box-shadow: none;
    color: var(--grey10);
    width: 100%;
    height: 100%;
    padding: .5rem 1rem;
    margin: -.5rem 0;
    text-align: left;
    display: inline-block;   
    position: relative;
    left: 0;
}

.datagrid-action-expandable:hover,
.datagrid-action-expandable:focus {
    background-color: transparent;
    left: .5rem;
    transition: left .3s;
    color: var(--grey10);
    box-shadow: none;
}

.datagrid-action-expandable .material-icons {
    margin-right: .5rem;
    color: var(--primary);
}

</style>