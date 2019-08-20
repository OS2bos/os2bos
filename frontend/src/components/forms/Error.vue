<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="danger error" v-if="msgs">
        <p v-for="m in msgs" :key="m[0]" class="error-msg">
            {{ m }}
        </p>
    </div>

</template>

<script>

    import notify from '../notifications/Notify.js'

    export default {

        props: [
            'msgs'
        ],
        methods: {
            handleError: function(error) {
                let msgs = {error: ['Der skete en fejl']}
                if (error.response) {
                    msgs = error.response.data // return the error JSON object
                    for (let m in msgs) {
                        notify(msgs[m][0], 'error')
                    }
                } else if (error.request) {
                    msgs = {error: [error.request.responseText]}
                    notify(msgs.error[0], 'error')
                } else if (error.message) {
                    msgs = {error: [error.message]}
                    notify(msgs.error[0], 'error')
                }
                return msgs
            }
        }

    }

</script>

<style>

    .error-msg {
        margin: .25rem 0;
    }

</style>