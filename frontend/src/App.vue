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
        opacity: 0.33;
    }

    .expected {
        color: hsl(var(--color3), 100%, 40%);
    }

    /* modal box */
    .modal-mask {
        position: fixed;
        z-index: 9998;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, .5);
        display: table;
        transition: opacity .3s ease;
    }

    .modal-wrapper {
        display: table-cell;
        vertical-align: middle;
    }

    .modal-container {
        max-width: 40rem;
        margin: 0px auto;
        padding: 3rem 3.5rem;
        background-color: var(--grey0);
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
        transition: all .3s ease;
        max-height: 90vh;
        max-width: 90vh;
        overflow-y: hidden;
        display: flex;
        flex-flow: column nowrap;
    }

    .modal-body {
        margin: 0.5rem 0;
        flex: 0 1 auto;
        overflow: scroll;
    }

    .modal-confirm-btn {
        float: right;
    }

    .modal-cancel-btn {
        float: right;
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

    .modal-enter {
        opacity: 0;
    }

    .modal-leave-active {
        opacity: 0;
    }

    .modal-enter .modal-container,
    .modal-leave-active .modal-container {
        -webkit-transform: scale(1.1);
        transform: scale(1.1);
    }

    .modal-form {
        background-color: none;
        padding: 0;
    }

</style>
