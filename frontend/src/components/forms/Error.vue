<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="danger error" v-if="errors">

        <p class="error-msg" v-for="e in errors[errKey]" v-if="errors[errKey]">
            {{ e }}
        </p>
        
        <template v-if="errKey === ''">
            <p class="error-msg error-generic" v-for="e in errors.detail" v-if="errors.detail">
                {{ e }}
            </p>
            <p class="error-msg error-generic" v-for="e in errors.non_field_errors" v-if="errors.non_field_errors">
                {{ e }}
            </p>
            <p class="error-msg error-generic" v-for="e in errors.errors" v-if="errors.errors">
                {{ e }}
            </p>
        </template>
    
    </div>

</template>

<script>

    import notify from '../notifications/Notify.js'

    export default {

        props: {
            errKey: {
                type: String,
                default: ''
            }
        },
        computed: {
            errors: function() {
                return this.$store.getters.getErrors
            }
        }

    }

</script>

<style>

    .error-msg {
        margin: .25rem 0;
    }

    .error-msg.error-generic {
        background-color: var(--danger);
        color: var(--grey0);
        padding: 1rem 2rem;
        margin: 0;
    }

    .error-msg.error-generic::before {
        content: '⚠';
        display: inline-block;
        margin: 0 .25rem 0 0;
        font-size: 1.25rem;
    }

</style>