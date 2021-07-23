<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="dialog modal-mask">
        <div class="modal-wrapper">
            <div class="modal-container">

                <div class="modal-header">
                    <slot name="header"></slot>
                    <button type="button" @click="close" title="Luk dialogbox" class="modal-close">
                        <i class="material-icons">close</i>
                    </button>
                </div>

                <div class="modal-body">
                    <slot name="body"></slot>
                </div>

                <div class="modal-footer">
                    <slot name="footer"></slot>
                </div>
            </div>
        </div>
    </div>

</template>

<script>

    export default {
        methods: {
            close: function() {
                this.$emit('closedialog')
            }
        }
    }

</script>

<style>

    .dialog .modal-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: space-between;
        border-bottom: solid 1px #ddd;
        padding-bottom: .5rem;
    }

    .dialog .modal-container {
        padding: 1rem 2rem 2rem;
    }

    .dialog .modal-footer {
        text-align: right;
        border-top: solid 1px #ddd;
    }

    .dialog .modal-footer button {
        margin-left: .5rem;
        margin-top: 1rem;
    }

    .dialog .modal-close {
        border: none;
        box-shadow: none;
        height: 2.5rem;
        width: 3rem;
        text-align: center;
        margin: 0 -1rem 0 0;
    }

</style>