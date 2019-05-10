<template>

    <form class="loginform" @submit.prevent="submitForm()">
        <h1>Log ind</h1>
        <fieldset>
            <label for="username">Brugernavn</label>
            <input type="text" id="username" placeholder="Brugernavn">
            <label for="password">Kodeord</label>
            <input type="password" id="password" placeholder="Kodeord">
        </fieldset>
        <fieldset>
            <input type="submit" value="Log ind">
        </fieldset>
    </form>

</template>

<script>
    
    export default {

        methods: {
            submitForm: function() {
                this.$router.push('/')
            }
        }

    }

</script>

<style>

    .loginform {
        margin: 1rem;
    }

</style>
