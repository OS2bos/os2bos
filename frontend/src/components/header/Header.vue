<template>

    <header>
        <nav class="globalheader">
            <router-link to="/">Mine sager</router-link>
            <router-link to="/login">Log ud</router-link>
        </nav>
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
        padding: 1rem;
        background-color: hsla(0,0%,0%,.1);
    }    

</style>
