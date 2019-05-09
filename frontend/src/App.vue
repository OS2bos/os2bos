<template>
    <div id="app">

        <app-header />
        
        <main>
            <router-view/>
        </main>

        <app-footer />

    </div>
</template>

<script>

    import AppHeader from './components/header/Header.vue'
    import AppFooter from './components/footer/Footer.vue'

    export default {
        components: {
            AppHeader,
            AppFooter
        }
    }

</script>

<style>

    #app {
        display: flex;
        flex-flow: column nowrap;
        width: 100%;
        height: 100%;
    }

    #app > main {
        flex: 1 0 auto;
    }

    .list {
        list-style: none;
        padding: 0;
        margin: 0;   
    }

    .list > li {
        padding: .5rem;
        border-top: solid 1px hsla(0,0%,0%,.25);
    }

</style>
