<template>

    <header class="globalheader">
        <router-link to="/">Mine sager</router-link>
        <router-link to="/login">Log ud</router-link>
    </header>

</template>

<script>
    
    export default {

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
