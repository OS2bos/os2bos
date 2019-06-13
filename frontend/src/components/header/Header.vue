<template>

    <header>
        <div class="globalheader">
            <h1 title="Ballerup Bevillingsplatformen">
                <router-link to="/" class="header-link">
                    <img class="global-logo" src="/logo.svg" alt="" />
                    <span>Ballerup <br>Bevillingsplatform</span>
                </router-link>
            </h1>
            <button v-if="auth" @click="logout()">Log ud</button>
        </div>
        <breadcrumb />
    </header> 

</template>

<script>

    import Breadcrumb from './Breadcrumb.vue'
    
    export default {

        components: {
            Breadcrumb
        },
        computed: {
            auth: function() {
                return this.$store.getters.getAuth
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

    .globalheader {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
        padding: 2rem;
        background-color: var(--grey0);
    }

    .globalheader > h1 {
        margin: 0;
        padding: 0;
    }

    .header-link {
        margin: 0;
        padding: 0;
        font-size: 1.125rem;
        color: #0b7ead;
        display: flex;
        flex-flow: row nowrap;
        border: none !important;
    }

    .global-logo {
        height: 2.5rem;
        width: auto;
        opacity: 1;
        margin: .25rem .5rem 0 0;
    }

</style>
