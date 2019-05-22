<template>

    <header>
        <div class="globalheader">
            <h1 title="Ballerup Bevillingsplatformen">
                <img class="global-logo" src="/logo.svg" alt="" />
                <span>Ballerup <br>Bevillingsplatform</span>
            </h1>
            <router-link to="/login">Log ud</router-link>
        </div>
        <breadcrumb />
    </header> 

</template>

<script>

    import Breadcrumb from './Breadcrumb.vue'
    
    export default {

        components: {
            Breadcrumb
        }

    }

</script>

<style>

    .globalheader {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
        padding: .75rem 1rem;
        background-color: var(--grey0);
    }

    .globalheader > h1 {
        margin: 0;
        padding: 0;
        font-size: 1.125rem;
        color: #0b7ead;
        display: flex;
        flex-flow: row nowrap;

    }

    .global-logo {
        height: 2.5rem;
        width: auto;
        opacity: 1;
        margin: .25rem .5rem 0 0;
    }

</style>
