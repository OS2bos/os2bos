<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


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
            this.$store.dispatch('autoLogin')
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
        min-width: 60rem;
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
        font-size: 2rem;
        vertical-align: middle;
    }

    .label {
        padding: .25rem .5rem;
        border-radius: .125rem;
        display: inline-block;
        text-transform: capitalize;
    }

    legend.required::after,
    label.required::after {
        content: "*";
        color: var(--danger);
        margin: 0 .25rem;
    }

    .mini-label .label {
        padding: .124rem .25rem;
        font-size: .85rem;
    }

    .label-DRAFT {
        background-color: var(--grey3);
        color: white;
    }

    .label-BUDGETED {
        background-color: var(--warning);
        color: white;
    }

    .label-EXPECTED {
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

    .danger {
        color: var(--danger);
    }

    .row {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        width: 100%;
    }

    .column {
        display: flex;
        flex-direction: column;
        flex-basis: 100%;
        flex: 1;
    }

    .table-heading {
        padding: .5rem 0 1rem 1.5rem;
    }

    .nowrap {
        white-space: nowrap;
    }

    .right {
        text-align: right;
    }    

    .dim {
        opacity: 0.33;
    }

    .expected {
        color: hsl(var(--color3), 100%, 50%);
    }

</style>
