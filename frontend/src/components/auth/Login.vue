<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <form class="loginform" @submit.prevent="submitForm()">
        <h1>Log ind</h1>
        <error />
        <fieldset>
            <label for="username">Brugernavn</label>
            <input type="text" id="username" placeholder="Brugernavn" v-model="username" autofocus required>
            <error err-key="username" />
            <label for="password">Kodeord</label>
            <input type="password" id="password" placeholder="Kodeord" v-model="password" required>
            <error err-key="password" />
        </fieldset>
        <fieldset>
            <input type="submit" value="Log ind">
        </fieldset>
    </form>

</template>

<script>

    import axios from '@/components/http/Http.js'
    import Error from '@/components/forms/Error.vue'
    
    export default {

        components: {
            Error
        },
        data: function() {
            return {
                username: null,
                password: null
            }
        },
        methods: {
            submitForm: function() {
                this.$store.dispatch('login', {
                    username: this.username,
                    password: this.password
                })
            }
        }

    }

</script>

<style>

    .loginform {
        margin: 2rem auto;
        max-width: 30rem;
    }

</style>
