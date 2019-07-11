<template>

    <div class="useractions" v-if="auth">
        <p style="margin: 0 1rem;">
            <strong>{{ user.username }}</strong><br> {{ team.name }}
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
                let user = this.$store.getters.getUser
                if (user) {
                    this.$store.dispatch('fetchTeam', user.team)
                }
                return user
            },
            team: function() {
                return this.$store.getters.getTeam
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
