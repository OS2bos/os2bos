<template>

    <form class="loginform" @submit.prevent="submitForm()">
        <h1>Log ind</h1>
        <fieldset>
            <label for="username">Brugernavn</label>
            <input type="text" id="username" placeholder="Brugernavn" v-model="username" required autofocus>
            <label for="password">Kodeord</label>
            <input type="password" id="password" placeholder="Kodeord" v-model="password" required>
        </fieldset>
        <fieldset>
            <input type="submit" value="Log ind">
        </fieldset>
    </form>

</template>

<script>

    import axios from '@/components/http/Http.js'
    
    export default {

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
