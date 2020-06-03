<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div id="app">

        <app-header />
        
        <main id="app-main">
            <router-view v-if="auth" />
            <article v-else class="noaccess">
                <h1>Adgang nægtet</h1>
                <p>Måske mangler du de rigtige rettigheder for at se denne side.</p>
            </article>
        </main>

        <app-footer />

        <browser-check />

    </div>
</template>

<script>

    import AppHeader from './components/header/Header.vue'
    import AppFooter from './components/footer/Footer.vue'
    import BrowserCheck from './components/browsercheck/Browsercheck.vue'

    export default {

        components: {
            AppHeader,
            AppFooter,
            BrowserCheck
        },
        computed: {
            auth: function() {
                return this.$store.getters.getAuth
            }
        }
        
    }

</script>

<style>

    #app {
        display: flex;
        flex-flow: column nowrap;
        width: 100%;
        min-width: 1024px;
        height: 100%;
    }

    #app > main {
        flex: 1 0 auto;
    }

    .noaccess {
        width: 30rem;
        height: 20rem;
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
        font-size: 2rem;
        vertical-align: middle;
    }

    .danger {
        color: var(--danger);
    }

    .row {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        width: 100%;
    }

    .row-item {
        flex: 1 0 30rem;
    }

    .column {
        display: flex;
        flex-direction: column;
        flex-basis: 100%;
        flex: 1;
    }

    .table-heading {
        padding: 1.25rem 0 .75rem 1.5rem;
    }

    .nowrap {
        white-space: nowrap;
    }

    .right {
        text-align: right;
    }    

    .dim {
        opacity: .6;
    }

    .expected {
        color: hsl(var(--color3), 100%, 28%);
    }

</style>
