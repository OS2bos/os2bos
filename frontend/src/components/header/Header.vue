<template>

    <header>
        <div class="globalheader">
            <h1>Bevillingssystemet</h1>
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
        padding: 1rem;
        background-color: var(--grey1);
    }
    .globalheader > h1 {
        padding: 0;
        opacity: .5;
        font-size: 1.25rem;
    }

</style>
