<template>

    <div class="useractions" v-if="auth">
        <p style="margin: 0 1rem;">
            Logget ind som <strong>{{ user.username }}</strong>
        </p>
        <button @click="logout()">Log ud</button>
    </div>

</template>

<script>
    
    export default {

        data: function() {
            return {

            }
        },
        computed: {
            auth: function() {
                return this.$store.getters.getAuth
            },
            user: function() {
                return this.$store.getters.getUser
            }
        },
        methods: {
            logout: function() {
                this.$store.dispatch('logout')
            }
        }

    }

</script>

<style>

    .useractions {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

</style>
