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
        },
        created: function() {
            this.$store.dispatch('fetchMunis')
            this.$store.dispatch('fetchDistricts')
            this.$store.dispatch('fetchActivities')
            this.$store.dispatch('fetchSections')
        }
        
    }

</script>

<style>

    form {
        background-color: var(--grey1);
        padding: .5rem 1rem;
    }

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
        padding: .75rem 0;
    }

    .material-icons {
        font-size: 3rem;
        vertical-align: middle;
    }

    .label {
        padding: .25rem .5rem;
        border-radius: .125rem;
        display: inline-block;
        text-transform: capitalize;
    }

    .label-DRAFT {
        background-color: var(--grey7);
        color: white;
    }

    .label-BUDGETED {
        background-color: var(--warning);
        color: white;
    }

    .label-GRANTED {
        background-color: var(--success);
        color: white;
    }

    .label-DISCONTINUED {
        background-color: var(--danger);
        color: white;
    }

</style>
